from secure_bridge import SecureBridge
import json
import os

def generate_and_save_keys():
    # Generar claves
    service1_secret, service1_public = SecureBridge.generate_curve_keypair()
    service2_secret, service2_public = SecureBridge.generate_curve_keypair()
    
    # Crear directorio para claves
    os.makedirs("keys", exist_ok=True)
    
    # Guardar claves en archivos separados
    keys = {
        "service1": {"secret": service1_secret, "public": service1_public},
        "service2": {"secret": service2_secret, "public": service2_public}
    }
    
    with open("keys/keys.json", "w") as f:
        json.dump(keys, f, indent=2)
    
    print("Claves generadas en ./keys/keys.json")
    return keys

if __name__ == "__main__":
    generate_and_save_keys()
