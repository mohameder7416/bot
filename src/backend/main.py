import sys
import os
from dotenv import load_dotenv
sys.path.append('..')
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from bot.agent.agent import Agent
from bot.models.groq_model import GroqModel
from bot.models.openai_model import OpenAIModel
from bot.models.ollama_model import OllamaModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info
from bot.variables import variables
# Load environment variables
load_dotenv()

app = FastAPI()




class AgentRequest(BaseModel):
    prompt: str
    model_service: str
    model_name: Optional[str] = None
    dealers_id: int  # Changed to int
    lead_id :int
    lead_crm_id : int 

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
        # Execute the agent's work
        result = agent.work(request.prompt)
        
        # Update variables.py with lead_id, lead_crm_id, and dealers_id
        variables.dealer_id = request.dealers_id
        variables.lead_id = request.lead_id
        variables.lead_crm_id = request.lead_crm_id
        
        return {
            "result": result,
            "dealers_id": variables.dealer_id,
           
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))