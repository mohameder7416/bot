import sys
sys.path.append('..')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from bot.models.groq_model import GroqModel
from bot.models.openai_model import OpenAIModel
from bot.models.ollama_model import OllamaModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info
from termcolor import colored

# Import your Agent class
from bot.agent.agent import Agent
app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    model_service: str
    model_name: str

class Response(BaseModel):
    response: str

# Initialize tools
tools = [get_dealers_info, get_products_info]

@app.post("/chat", response_model=Response)
async def chat(request: ChatRequest):
    try:
        # Determine the model service based on the request
        if request.model_service.lower() == "openai":
            model_service = OpenAIModel
        elif request.model_service.lower() == "groq":
            model_service = GroqModel
        elif request.model_service.lower() == "ollama":
            model_service = OllamaModel
        else:
            raise ValbmmueError(f"Unsupported model service: {request.model_service}")

        # Initialize the agent with the requested model service and name
        agent = Agent(
            tools=tools, 
            model_service=model_service, 
            model_name=request.model_name,
            stop=None  # You might want to make this configurable as well
        )

        result = agent.work(request.prompt)
        return Response(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

