from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import ask


app=FastAPI(title="NLP SQL Agent",version="1.0.0")

class Query(BaseModel):
    query:str
    history:list[dict]|None=None

@app.post("/query")
async def query(req:Query):
    result=ask(req.query,req.history)
    return result

@app.get("/")
def health():
    return {"status":"healthy"}



