from .MongoConnection import MongoConnection
import base64
from datetime import datetime, timezone
import os

def guardar_imagen(ruta_img_jpg: str, producto_id) -> None:
    # Convierte a int por si viene como Decimal u otro tipo
    producto_id = int(producto_id)

    mongo = MongoConnection()
    collection = mongo.get_collection()

    with open(ruta_img_jpg, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')

    new_doc = {
        "producto_id": producto_id,     # ahora es un int
        "imagen":      encoded,
        "modified_date": datetime.now(timezone.utc)
    }
    collection.insert_one(new_doc)
    print("Imagen guardada en MongoDB.")

    # opcional: eliminar el fichero local
    try:
        os.remove(ruta_img_jpg)
        print(f"Imagen local '{ruta_img_jpg}' eliminada.")
    except Exception as e:
        print(f"No se pudo eliminar la imagen local: {e}")

"""
def guardar_imagen(ruta_img_jpg: str, producto_id: int) -> None:
    mongo = MongoConnection()
    collection = mongo.get_collection()

    with open(ruta_img_jpg, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')

    new_doc = {
        "producto_id": producto_id,     # <— ahora lo indexamos por ProductoID
        "imagen":      encoded,
        "modified_date": datetime.now(timezone.utc)
    }
    collection.insert_one(new_doc)
    print("Imagen guardada en MongoDB.")

    try:
        os.remove(ruta_img_jpg)
        print(f"Imagen local '{ruta_img_jpg}' eliminada.")
    except Exception as e:
        print(f"No se pudo eliminar la imagen local: {e}")
"""
"""
def guardar_imagen(ruta_img_jpg: str) -> str :
    mongo = MongoConnection()
    collection_images = mongo.get_collection()

    with open(ruta_img_jpg, 'rb') as img_file:
        encoded_img_string = base64.b64encode(img_file.read()).decode('utf-8')

    nombre_img = os.path.splitext(os.path.basename(ruta_img_jpg))[0]
    new_document = {
        "nombre": nombre_img,
        "imagen": encoded_img_string,
        "modified_date": datetime.now(timezone.utc)
    }

    collection_images.insert_one(new_document)
    print("Imagen guardada en MongoDB.")

    try:
        os.remove(ruta_img_jpg)
        print(f"Imagen local '{ruta_img_jpg}' eliminada.")
    except Exception as e:
        print(f"No se pudo eliminar la imagen local: {e}")

    return nombre_img
"""