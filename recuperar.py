from .MongoConnection import MongoConnection
import base64
from PIL import Image
from io import BytesIO

def recuperar_imagen(producto_id: int) -> Image.Image:
    mongo = MongoConnection()
    coll  = mongo.get_collection()
    doc = coll.find_one({"producto_id": producto_id})
    if doc and doc.get("imagen"):
        img = Image.open(BytesIO(base64.b64decode(doc["imagen"])))
        return img
    # placeholder
    return Image.new("RGB", (80,80), (200,200,200))

"""
# recuperar.py
from MongoConnection import MongoConnection
import base64
from PIL import Image
from io import BytesIO

def recuperar_imagen(nombre_img: str) -> Image.Image:
    mongo = MongoConnection()
    collection = mongo.get_collection()

    doc = collection.find_one({"nombre": nombre_img})
    if doc and doc.get('imagen'):
        data = base64.b64decode(doc['imagen'])
        img = Image.open(BytesIO(data))
        return img
    else:
        # Placeholder gris 80×80
        placeholder = Image.new('RGB', (80,80), (200,200,200))
        return placeholder
"""
"""
from MongoConnection import MongoConnection
import base64
from PIL import Image # py -m pip install pillow
from io import BytesIO

def recuperar_imagen(nombre_img: str):
    mongo = MongoConnection()
    collection_images = mongo.get_collection()

    document = collection_images.find_one({"nombre": nombre_img})

    if(document):
        imagen_base64 = document['imagen'] #columna/atributo 'imagen' del documento
        imagen_bytes = base64.b64decode(imagen_base64)
        imagen = Image.open(BytesIO(imagen_bytes))
        imagen.save(f"../images-recuperadas/{nombre_img}_recuperada.jpg")
        print(f"Imagen guardada como {nombre_img}_recuperada.jpg")
        imagen.show()
    else:
        print("No se encontró ninguna imagen en la base de datos.")
"""