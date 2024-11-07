import faiss
import numpy as np
import pickle
import os

class VectorDB:
    def __init__(self, dimension, index_file='data/index.faiss', metadata_file='data/metadata.pkl'):
        self.dimension = dimension
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []

        os.makedirs(os.path.dirname(index_file), exist_ok=True)

        if os.path.exists(index_file) and os.path.exists(metadata_file):
            self.load()
        else:
            self.save()

    def add_embeddings(self, embeddings, metadata):
        embeddings_np = np.array(embeddings).astype('float32')
        self.index.add(embeddings_np)
        self.metadata.extend(metadata)
        self.save()

    def search(self, embedding, k=5):
        D, I = self.index.search(np.array([embedding]).astype('float32'), k)
        resultados = []
        for idx in I[0]:
            resultado = {
                'fragmento': self.metadata[idx]['fragmento'],
                'archivo': self.metadata[idx]['archivo']
            }
            resultados.append(resultado)
        return resultados

    def save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)

    def load(self):
        self.index = faiss.read_index(self.index_file)
        with open(self.metadata_file, 'rb') as f:
            self.metadata = pickle.load(f)
    
    def limpiar_fragmentos_largos(self, max_length=800):
        # Filtrar los metadatos para excluir los fragmentos que excedan el tamaño máximo
        fragmentos_filtrados = [
            metadata for metadata in self.metadata if len(metadata['fragmento']) <= max_length
        ]
        
        # Actualizar la lista de metadatos y el índice
        if len(fragmentos_filtrados) < len(self.metadata):
            print(f"Eliminando {len(self.metadata) - len(fragmentos_filtrados)} fragmentos que exceden {max_length} caracteres.")
            self.metadata = fragmentos_filtrados
            
            # Crear un nuevo índice solo con los fragmentos válidos
            embeddings_filtrados = [
                self.index.reconstruct(idx) for idx, metadata in enumerate(self.metadata) if len(metadata['fragmento']) <= max_length
            ]
            
            # Borrar el índice actual y recrearlo
            self.index.reset()
            self.index.add(np.array(embeddings_filtrados).astype('float32'))
            self.save()  # Guardar los cambios

        else:
            print("No se encontraron fragmentos que excedan el tamaño máximo.")

    def vaciar_base_de_datos(self):
        # Reiniciar el índice FAISS
        self.index.reset()
        # Vaciar los metadatos
        self.metadata = []
        # Guardar el estado vacío
        self.save()
        print("La base de datos ha sido vaciada.")