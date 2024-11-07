from fastapi import FastAPI
from app.api import router
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://llm-chatbot-ten.vercel.app"],  # Permite el frontend de React
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)
app.include_router(router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Incluir esta parte solo cuando estás corriendo localmente
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000)) 
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
