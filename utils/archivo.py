MAX_MB = 200

def validar_tamano(archivo):
    max_bytes = MAX_MB * 1024 * 1024
    if archivo.size > max_bytes:
        raise ValueError(f"Archivo mayor a {MAX_MB}")
    
def extension_valida(nombre):
    return nombre.lower().endswith((".csv",".xlsx"))

def nombre_salida(nombre_original, sufijo):
    base = nombre_original.rsplit(".",1)[0]
    return f"{base}_{sufijo}"