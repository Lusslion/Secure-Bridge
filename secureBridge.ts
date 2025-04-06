import * as zmq from "zeromq";
import * as jwt from "jsonwebtoken";
import * as fs from "fs";
import * as msgpack from "msgpack-lite";
import * as protobuf from "protobufjs"; // Para Protobuf
import { CircuitBreaker } from "opossum";
import * as client from "prom-client";
import * as express from "express";
import { createLogger, format, transports } from "winston";

// Winston logger
const logger = createLogger({
  format: format.json(),
  transports: [new transports.Console()],
});

// Métricas Prometheus
const requestCount = new client.Counter({
  name: "requests_total",
  help: "Número total de solicitudes",
  labelNames: ["operation"],
});
const requestLatency = new client.Histogram({
  name: "request_latency_seconds",
  help: "Latencia de solicitudes",
  labelNames: ["operation"],
});

// Servidor Prometheus
const app = express();
app.get("/metrics", async (req, res) => {
  res.set("Content-Type", client.register.contentType);
  res.end(await client.register.metrics());
});
app.listen(8000, () => console.log("Prometheus metrics available on /metrics"));

interface Handler {
  (data: any): any;
}

function BridgeHandler(operation: string) {
  return (target: any, key: string) => {
    if (!target.constructor.handlers) {
      target.constructor.handlers = new Map();
    }
    target.constructor.handlers.set(operation, target[key]);
  };
}

export class SecureBridge {
  private serverSocket: zmq.Reply | null = null;
  private clientSocket: zmq.Request | null = null;
  private handlers: Map<string, Handler> = new Map();
  private jwtSecret: string;
  private circuitBreaker: CircuitBreaker;

  constructor(
    private serverPort: number,
    private clientPort: number,
    private privateKey: string,
    private publicKey: string,
    private peerPublicKey: string,
    jwtSecret: string
  ) {
    this.jwtSecret = jwtSecret;
    this.circuitBreaker = new CircuitBreaker(this.sendRequest.bind(this), {
      errorThresholdPercentage: 50,
      resetTimeout: 30000,
    });
  }

  registerHandler(operation: string, handler: Handler) {
    this.handlers.set(operation, handler);
  }

  validateJwt(token: string): any {
    try {
      return jwt.verify(token, this.jwtSecret);
    } catch (error) {
      throw new Error("Invalid JWT");
    }
  }

  serialize(data: object, format: string): Buffer {
    if (format === "protobuf") {
      const message = BridgeMessage.create(data); // Clase generada por Protobuf
      return BridgeMessage.encode(message).finish();
    }
    if (format === "json") {
      return Buffer.from(JSON.stringify(data));
    } else if (format === "msgpack") {
      return msgpack.encode(data);
    } else {
      throw new Error("Unsupported serialization format");
    }
  }

  deserialize(data: Buffer, format: string): any {
    if (format === "protobuf") {
      const message = BridgeMessage.decode(data); // Clase generada por Protobuf
      return BridgeMessage.toObject(message);
    }
    if (format === "json") {
      return JSON.parse(data.toString());
    } else if (format === "msgpack") {
      return msgpack.decode(data);
    } else {
      throw new Error("Unsupported serialization format");
    }
  }

  @BridgeHandler("sum")
  public handleSum(data: any): any {
    return { result: data.a + data.b };
  }

  async startServer() {
    this.serverSocket = new zmq.Reply();
    this.serverSocket.curve_server = true;
    this.serverSocket.curve_secretkey = this.privateKey;
    this.serverSocket.curve_publickey = this.publicKey;

    await this.serverSocket.bind(`tcp://*:${this.serverPort}`);
    console.log(`Server listening on port ${this.serverPort}`);

    for await (const [msg] of this.serverSocket) {
      const start = Date.now();
      try {
        const message = JSON.parse(msg.toString());
        const token = message.token;
        this.validateJwt(token);
        const operation = message.operation;
        requestCount.inc({ operation });
        const handler = this.handlers.get(operation);
        if (handler) {
          const response = handler(message.data);
          await this.serverSocket.send(
            JSON.stringify({ status: "success", data: response })
          );
        } else {
          throw new Error("Unknown operation");
        }
        requestLatency.observe({ operation }, (Date.now() - start) / 1000);
      } catch (error) {
        logger.error("Server error", { error: error.message });
        await this.serverSocket.send(
          JSON.stringify({ status: "error", message: error.message })
        );
      }
    }
  }

  async sendRequest(message: object, format: string = "json"): Promise<any> {
    if (!this.clientSocket) throw new Error("Client socket not initialized");
    const serializedMessage = this.serialize(message, format);
    await this.clientSocket.send(serializedMessage);
    const [response] = await this.clientSocket.receive();
    return this.deserialize(response, format);
  }

  async startClient(message: object, format: string = "json") {
    this.clientSocket = new zmq.Request();
    this.clientSocket.curve_serverkey = this.peerPublicKey;
    this.clientSocket.curve_secretkey = this.privateKey;
    this.clientSocket.curve_publickey = this.publicKey;

    await this.clientSocket.connect(`tcp://localhost:${this.clientPort}`);
    console.log(`Client connected to port ${this.clientPort}`);

    try {
      return await this.circuitBreaker.fire(message, format);
    } catch (error) {
      console.error("Client error:", error);
      return { status: "error", message: error.message };
    }
  }

  async shutdown() {
    if (this.serverSocket) {
      await this.serverSocket.close();
    }
    if (this.clientSocket) {
      await this.clientSocket.close();
    }
  }
}
