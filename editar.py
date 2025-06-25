from pymongo import MongoClient
import base64
from PIL import Image
from io import BytesIO
import os
from datetime import datetime
from .MongoConnection import MongoConnection

def editar_imagen(producto_id: int, ruta_img: str) -> None:
    """
    Reemplaza la imagen existente de un producto en MongoDB.
    Si no existe, la inserta. Elimina el archivo local tras la operación.
    """
    mc = MongoConnection()
    coll = mc.get_collection()

    # Leer y codificar imagen
    with open(ruta_img, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')

    # Intentar actualizar documento existente
    result = coll.update_one(
        { 'producto_id': int(producto_id) },
        { '$set': { 'imagen': encoded, 'modified_date': datetime.utcnow() } },
        upsert=True
    )

    if result.matched_count:
        print(f"Imagen de producto {producto_id} actualizada en MongoDB.")
    else:
        print(f"No se encontró imagen previa para producto {producto_id}. Se insertó nueva.")

    # Eliminar archivo local
    try:
        os.remove(ruta_img)
        print(f"Archivo local '{ruta_img}' eliminado.")
    except Exception as e:
        print(f"Error eliminando archivo local: {e}")
