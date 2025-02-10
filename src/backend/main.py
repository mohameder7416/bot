from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

# Import the process_and_query function
from rag_llm import process_and_query  # Replace 'your_module' with the actual module name

app = FastAPI()

class Query(BaseModel):
    text: str

class Response(BaseModel):
    answer: str

@app.post("/chat", response_model=Response)
async def query_endpoint(query: Query):
    result = process_and_query(query.text)
    return Response(answer=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)