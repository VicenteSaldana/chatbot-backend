import requests
import json
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def contar_tokens_aproximado(texto):
    """
    Cuenta los tokens aproximados basándose en el número de caracteres.
    Asume que 1 token ≈ 4 caracteres.
    """
    return len(texto) // 4

def truncar_contexto_por_palabras(contexto, max_tokens):
    """
    Trunca el contexto asegurando que no se corten palabras a la mitad.
    """
    palabras = contexto.split()
    contexto_truncado = ""
    tokens = contar_tokens_aproximado(contexto_truncado)
    
    for palabra in palabras:
        prueba = f"{contexto_truncado} {palabra}".strip()
        tokens_prueba = contar_tokens_aproximado(prueba)
        if tokens_prueba > max_tokens:
            break
        contexto_truncado = prueba
        tokens = tokens_prueba
    
    return contexto_truncado

def obtener_respuesta_LLM(contexto, consulta, max_tokens=1200):
    url = 'http://tormenta.ing.puc.cl/api/generate'
    prompt = f"Contexto:\n{contexto}\n\nPregunta:\n{consulta}\n\nRespuesta:"

    num_tokens = contar_tokens_aproximado(prompt)
    logging.info(f"Tamaño del prompt: {len(prompt)} caracteres, aproximadamente {num_tokens} tokens.")

    # Truncar el contexto si es necesario
    if num_tokens > max_tokens:
        contexto_truncado = truncar_contexto_por_palabras(contexto, max_tokens)
        prompt = f"Contexto:\n{contexto_truncado}\n\nPregunta:\n{consulta}\n\nRespuesta:"
        num_tokens = contar_tokens_aproximado(prompt)
        logging.info(f"Contexto truncado a {len(contexto_truncado)} caracteres, nuevo tamaño del prompt: {len(prompt)} caracteres, aproximadamente {num_tokens} tokens.")
        print(f"Prompt truncado: {len(prompt)} caracteres, aproximadamente {num_tokens} tokens.")

    payload = {
        "model": "integra-LLM",
        "prompt": prompt
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Realizar la solicitud con streaming habilitado
        response = requests.post(url, json=payload, headers=headers, stream=True, timeout=120)

        if response.status_code != 200:
            logging.error(f"Error al obtener respuesta del LLM: {response.status_code} - {response.text}")
            print(f"Error al obtener respuesta del LLM: {response.status_code} - {response.text}")
            return "Lo siento, no puedo procesar tu solicitud en este momento."

        # Verificar el tipo de contenido
        content_type = response.headers.get('Content-Type', '')
        logging.info(f"Content-Type de la respuesta: {content_type}")
        if 'application/x-ndjson' not in content_type.lower():
            logging.warning("El Content-Type de la respuesta no es 'application/x-ndjson', pero se intentará procesar la respuesta.")

        # Procesar la respuesta NDJSON
        respuesta_completa = ""
        for line_number, line in enumerate(response.iter_lines(), start=1):
            if line:
                try:
                    # Decodificar la línea
                    decoded_line = line.decode('utf-8')
                    logging.debug(f"Línea {line_number} recibida: {decoded_line}")
                    # Parsear el JSON de la línea
                    data = json.loads(decoded_line)
                    # Concatenar el fragmento de la respuesta
                    fragmento = data.get('response', '')
                    respuesta_completa += fragmento
                    # Verificar si la respuesta está completa
                    if data.get('done', False):
                        logging.info("Finalización de la respuesta detectada.")
                        break
                except json.JSONDecodeError as e:
                    logging.error(f"Error al decodificar la línea JSON en la línea {line_number}: {e}")
                    logging.error(f"Línea recibida: {decoded_line}")
                    return "Lo siento, no puedo procesar tu solicitud en este momento."

        logging.info("Respuesta del LLM obtenida exitosamente.")
        return respuesta_completa.strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Excepción al obtener respuesta del LLM: {e}")
        print(f"Excepción al obtener respuesta del LLM: {e}")
        return "Lo siento, no puedo procesar tu solicitud en este momento."
