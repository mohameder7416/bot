from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sys 
import asyncio
sys.path.append('..')
import os
from dotenv import load_dotenv
from bot.agent.agent import Agent
from bot.models.openai_model import OpenAIModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info
from bot.tools.make_appointment import make_appointment
from bot.variables.variables import variables, load_variables, save_variables

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
    stream: Optional[bool] = True  # Add streaming option, default to True

@app.post("/api/webhook-agent")
async def run_agent(request: AgentRequest):
    tools = [get_dealers_info, get_products_info, make_appointment]
    
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
        
        # Check if streaming is requested
        if request.stream:
            # Execute the agent's work with streaming
            return await agent.work_stream(request.prompt)
        else:
            # Execute the agent's work without streaming
            result = await agent.work(request.prompt)
            return JSONResponse(content={"result": result})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))