from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

app = FastAPI()

# Modelo para la entrada (POST/PUT)
class AvisoIn(BaseModel):
    titulo: str
    contenido: str

# Modelo para la salida (GET)
class AvisoOut(BaseModel):
    id: int
    titulo: str
    contenido: str
    creado_en: datetime
    actualizado_en: datetime

# Almacenamiento en memoria
avisos: List[Dict] = []
id_counter = 1

# Endpoint para obtener todos los avisos
@app.get("/avisos", response_model=List[AvisoOut])
def obtener_avisos():
    return avisos

# Endpoint para crear un nuevo aviso
@app.post("/avisos", response_model=AvisoOut)
def agregar_aviso(aviso: AvisoIn):
    global id_counter
    nuevo_aviso = {
        "id": id_counter,
        "titulo": aviso.titulo,
        "contenido": aviso.contenido,
        "creado_en": datetime.now(),
        "actualizado_en": datetime.now()
    }
    avisos.append(nuevo_aviso)
    id_counter += 1
    return nuevo_aviso

# Endpoint para obtener un aviso específico 
@app.get("/avisos/{aviso_id}", response_model=AvisoOut)
def obtener_aviso(aviso_id: int):
    for aviso in avisos:
        if aviso["id"] == aviso_id:
            if "creado_en" not in aviso:
                aviso["creado_en"] = datetime.now()
            if "actualizado_en" not in aviso:
                aviso["actualizado_en"] = datetime.now()
            return aviso
    raise HTTPException(status_code=404, detail="Aviso no encontrado")

# Endpoint para actualizar un aviso 
@app.put("/avisos/{aviso_id}", response_model=AvisoOut)
def actualizar_aviso(aviso_id: int, aviso_actualizado: AvisoIn):
    global avisos
    for index, aviso in enumerate(avisos):
        if aviso["id"] == aviso_id:
            avisos[index] = {
                "id": aviso_id,
                "titulo": aviso_actualizado.titulo,
                "contenido": aviso_actualizado.contenido,
                "creado_en": aviso["creado_en"],  #conservar fecha original
                "actualizado_en": datetime.now()
            }
            return avisos[index]
    raise HTTPException(status_code=404, detail="Aviso no encontrado")
    
# Endpoint para eliminar un aviso
@app.delete("/avisos/{aviso_id}")
def eliminar_aviso(aviso_id: int):
    global avisos
    for aviso in avisos:
        if aviso["id"] == aviso_id:
            avisos.remove(aviso)
            return {"mensaje": "Aviso eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Aviso no encontrado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="172.21.112.1", port=8000)
