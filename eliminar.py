from pymongo import MongoClient

def eliminar_imagen(producto_id: int) -> bool:
    """
    Elimina la imagen de un producto en MongoDB.
    Retorna True si se eliminó al menos un documento, False si no se encontró.
    """
    mc = MongoClient('mongodb://localhost:27017/')
    coll = mc['marketplace-images']['images']

    result = coll.delete_one({ 'producto_id': int(producto_id) })
    if result.deleted_count > 0:
        print(f"Imagen de producto {producto_id} eliminada de MongoDB.")
        return True
    else:
        print(f"No se encontró imagen para producto {producto_id} en MongoDB.")
        return False
