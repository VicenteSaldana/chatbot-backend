import requests
import json
def obtener_embedding(texto):
    url = 'http://tormenta.ing.puc.cl/api/embed'
    payload = {
        "model": "nomic-embed-text",
        "input": json.dumps(texto)[1:-1]
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data['embeddings'][0]
    else:
        print("Error al obtener embedding:", response.text)
        return None
