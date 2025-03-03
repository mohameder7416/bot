from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
import sys 
sys.path.append('..')
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from bot.agent.agent import Agent
from bot.models.openai_model import OpenAIModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info
from bot.tools.make_appointment import make_appointment
from bot.variables.variables import variables, load_variables, save_variables
from bot.utils.chat_history import save_conversation
from bot.utils.db import DataBase
DB_USER_WRITE= os.getenv("DB_USER_WRITE")
DB_PASSWORD_WRITE = os.getenv("DB_PASSWORD_WRITE")
DB_HOST_WRITE = os.getenv("DB_HOST_WRITE")
DB_PORT_WRITE = os.getenv("DB_PORT_WRITE")
DB_NAME_WRITE = os.getenv("DB_NAME_WRITE")

db = DataBase(host=DB_HOST_WRITE,user=DB_USER_WRITE,password=DB_PASSWORD_WRITE,database=DB_NAME_WRITE,port=3306)




# Load environment variables
load_dotenv()

app = FastAPI()

class AgentRequest(BaseModel):
    prompt: str
    model_service: str
    model_name: Optional[str] = None
    dealers_id: int
    lead_id: int
    lead_crm_id: int
    product_id: Optional[int] = None  # Make product_id optional

@app.post("/agent")
async def run_agent(request: AgentRequest):
    tools = [get_dealers_info, get_products_info,make_appointment]
    
    model_service_map = {
        "openai": OpenAIModel
    }
    
    if request.model_service not in model_service_map:
        raise HTTPException(status_code=400, detail="Invalid model service")
    
    model_service = model_service_map[request.model_service]
    
    stop = None if request.model_service != "ollama" else ["\n", "Human:", "Assistant:"]
    
    agent = Agent(tools=tools, model_service=model_service, model_name=request.model_name, stop=stop)
    
    try:
        # Load current variables
        current_vars = load_variables()
        
        # Update variables with request data
        current_vars["lead_id"] = request.lead_id
        current_vars["dealer_id"] = request.dealers_id
        current_vars["lead_crm_id"] = request.lead_crm_id
        if request.product_id is not None:
            current_vars["product_id"] = request.product_id
        
        # Save updated variables
        save_variables(current_vars)
        
        # Update variables in the bot
        variables.dealer_id = request.dealers_id
        variables.lead_id = request.lead_id
        variables.lead_crm_id = request.lead_crm_id
        if request.product_id is not None:
            variables.product_id = request.product_id
        
        # Execute the agent's work
        result = agent.work(request.prompt)
        save_conversation(db,variables.lead_id,request.prompt,result)
        
        return {
            "result": result,
            "dealers_id": variables.dealer_id,
            "lead_id": variables.lead_id,
            "lead_crm_id": variables.lead_crm_id,
            "product_id": variables.product_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
