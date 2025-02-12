import sys 
sys.path.append('..')
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from bot.agent.agent import Agent
from bot.models.groq_model import GroqModel
from bot.models.openai_model import OpenAIModel
from bot.models.ollama_model import OllamaModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info

app = FastAPI()

class AgentRequest(BaseModel):
    prompt: str
    model_service: str
    model_name: Optional[str] = None

@app.post("/agent")
async def run_agent(request: AgentRequest):
    tools = [get_dealers_info, get_products_info]
    
    model_service_map = {
        "openai": OpenAIModel,
        "groq": GroqModel,
        "ollama": OllamaModel
    }
    
    if request.model_service not in model_service_map:
        raise HTTPException(status_code=400, detail="Invalid model service")
    
    model_service = model_service_map[request.model_service]
    
    stop = None if request.model_service != "ollama" else ["\n", "Human:", "Assistant:"]
    
    agent = Agent(tools=tools, model_service=model_service, model_name=request.model_name, stop=stop)
    
    try:
        result = agent.work(request.prompt)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



