import * as swaggerUi from "swagger-ui-express";
import * as swaggerJsDoc from "swagger-jsdoc";
import * as express from "express";

const app = express();

const swaggerOptions = {
  swaggerDefinition: {
    openapi: "3.0.0",
    info: {
      title: "Bridge API",
      version: "1.0.0",
    },
  },
  apis: ["./secureBridge.ts"],
};

const swaggerDocs = swaggerJsDoc(swaggerOptions);
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocs));

app.listen(3000, () => console.log("Swagger docs available on /api-docs"));
