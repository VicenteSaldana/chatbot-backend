import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .embeddings import obtener_embedding
from .database import VectorDB

def almacenar_en_vectordb(embeddings, fragmentos, metadata_fragmentos):
    # Agregar los fragmentos al metadata
    for i, fragmento in enumerate(fragmentos):
        metadata_fragmentos[i]['fragmento'] = fragmento

    print(f"Almacenando {len(embeddings)} embeddings en la base de datos")
    dimension = 768  # Dimensionalidad del embedding
    vectordb = VectorDB(dimension)

    vectordb.add_embeddings(embeddings, metadata_fragmentos)

def generar_embeddings(fragmentos):
    embeddings = []
    for idx, fragmento in enumerate(fragmentos):
        print(f"Generando embedding para el fragmento {idx+1}/{len(fragmentos)}")
        embedding = obtener_embedding(fragmento)
        if embedding:
            embeddings.append(embedding)
        else:
            embeddings.append([0]*768)  # Vector nulo en caso de error
    return embeddings

def cargar_guiones(directorio):
    guiones = {}
    for archivo in os.listdir(directorio):
        if archivo.endswith('.txt'):
            with open(os.path.join(directorio, archivo), 'r', encoding='utf-8') as f:
                texto = f.read()
                guiones[archivo] = texto
    return guiones

def limpiar_texto(texto):
    # Elimina etiquetas HTML y caracteres especiales
    texto_limpio = re.sub(r'<[^>]+>', '', texto)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    texto_limpio = texto_limpio.strip()
    return texto_limpio

def dividir_en_fragmentos(text):
    fragment_size = 800
    words = text.split()
    fragments = [" ".join(words[i:i + fragment_size]) for i in range(0, len(words), fragment_size)]
    return fragments

def procesar_guiones(directorio_scripts):
    guiones = cargar_guiones(directorio_scripts)
    todos_los_fragmentos = []
    metadata_fragmentos = []
    for nombre_archivo, texto in guiones.items():
        print(f"Procesando el guion: {nombre_archivo}")
        texto_limpio = limpiar_texto(texto)
        fragmentos = dividir_en_fragmentos(texto_limpio)
        print(f"Generados {len(fragmentos)} fragmentos del guion {nombre_archivo}")
        todos_los_fragmentos.extend(fragmentos)
        metadata_fragmentos.extend([{'archivo': nombre_archivo}] * len(fragmentos))
    return todos_los_fragmentos, metadata_fragmentos

def procesar_y_almacenar_todo(directorio_scripts):
    fragmentos, metadata_fragmentos = procesar_guiones(directorio_scripts)
    embeddings = generar_embeddings(fragmentos)
    almacenar_en_vectordb(embeddings, fragmentos, metadata_fragmentos)