from fastapi import APIRouter
from pydantic import BaseModel
from .database import VectorDB
from .embeddings import obtener_embedding
from .llm import obtener_respuesta_LLM
import re

router = APIRouter()

class Consulta(BaseModel):
    consulta: str

def identificar_pelicula(consulta):
    # Lista de títulos de películas conocidos
    peliculas = ["apt-pupil", "argo", "assassins", "buried", "carrie", "gravity", "heist", "lord-of-war", "psycho", "south-park", "Apt Pupil", "apt pupil", "Argo", "Assassins", "Buried", "Carrie", "Gravity", "Heist", "Lord of War", "Psycho", "South Park", "south park", "lord of war"]
    
    # Buscar el título de la película en la consulta
    for pelicula in peliculas:
        if re.search(r'\b' + re.escape(pelicula) + r'\b', consulta, re.IGNORECASE):
            return pelicula
    return None

@router.post('/consulta')
def procesar_consulta(consulta: Consulta):
    import logging
    logging.basicConfig(level=logging.INFO)

    vectordb = VectorDB(768)
    embedding_consulta = obtener_embedding(consulta.consulta)

    if not embedding_consulta:
        logging.error("No se pudo obtener el embedding de la consulta.")
        return {'respuesta': "Lo siento, no puedo procesar tu solicitud en este momento."}
    
    # Identificar si la consulta menciona una película específica
    peliculas = ["apt-pupil", "argo", "assassins", "buried", "carrie", "gravity", "heist", "lord-of-war", "psycho", "south-park", "Apt Pupil", "apt pupil", "Argo", "Assassins", "Buried", "Carrie", "Gravity", "Heist", "Lord of War", "Psycho", "South Park", "south park", "lord of war"]
    pelicula_especifica = next((pelicula for pelicula in peliculas if pelicula in consulta.consulta.lower()), None)

    # Realizar la búsqueda en la base de datos de vectores
    resultados = vectordb.search(embedding_consulta, k=5)

    # Si se menciona una película, priorizar fragmentos de esa película
    if pelicula_especifica:
        resultados = [res for res in resultados if pelicula_especifica in res['fragmento'].lower()] + resultados
        resultados = resultados[:5]

    for idx, resultado in enumerate(resultados, start=1):
        logging.info(f"Fragmento {idx}: {resultado['fragmento']}")

    contexto = ' '.join([r['fragmento'] for r in resultados])
    logging.info(f"Contexto construido con {len(resultados)} fragmentos.")
    
    # Verificar el tamaño del contexto
    num_tokens = len(contexto) // 4
    logging.info(f"Tamaño del contexto: {len(contexto)} caracteres, aproximadamente {num_tokens} tokens.")
    
    # Limitar el contexto si es necesario
    max_tokens = 2000
    if num_tokens > max_tokens:
        excess = num_tokens - max_tokens
        trunc_length = excess * 4  # Aproximadamente 4 caracteres por token
        contexto = contexto[:-trunc_length].rsplit('.', 1)[0] + '.'
        logging.info(f"Contexto truncado a {len(contexto)} caracteres.")
    
    respuesta = obtener_respuesta_LLM(contexto, consulta.consulta)
    
    return {'respuesta': respuesta}
