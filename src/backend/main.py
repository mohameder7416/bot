# File: main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import json
import sys 
sys.path.append('..')
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from bot.agent.agent import Agent
from bot.models.groq_model import GroqModel
from bot.models.openai_model import OpenAIModel
from bot.models.ollama_model import OllamaModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info
from bot.tools.make_appointment import make_appointment
from bot.variables.variables import variables, load_variables, save_variables
from datetime import datetime

load_dotenv()

app = FastAPI()

# Database setup
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    prompt = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_chat_history(db: Session, lead_id: int, prompt: str, response: str):
    db_chat = ChatHistory(lead_id=lead_id, prompt=prompt, response=response)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_chat_history(db: Session, lead_id: int, limit: int = 10):
    return db.query(ChatHistory).filter(ChatHistory.lead_id == lead_id).order_by(ChatHistory.timestamp.desc()).limit(limit).all()




class AgentRequest(BaseModel):
    prompt: str
    model_service: str
    model_name: Optional[str] = None
    dealers_id: int
    lead_id: int
    lead_crm_id: int
    product_id: Optional[int] = None

@app.post("/agent")
async def run_agent(request: AgentRequest, db: Session = Depends(get_db)):
    tools = [get_dealers_info, get_products_info, make_appointment]
    
    model_service_map = {
        "openai": OpenAIModel,
        "groq": GroqModel,
        "ollama": OllamaModel
    }
    
    if request.model_service not in model_service_map:
        raise HTTPException(status_code=400, detail="Invalid model service")
    
    model_service = model_service_map[request.model_service]
    
    stop = None if request.model_service != "ollama" else ["\n", "Human:", "Assistant:"]
    
    # Retrieve chat history
    chat_history = get_chat_history(db, request.lead_id)
    default_model_name = "gpt-4o" if request.model_service == "openai" else None
    # Create model instance with chat history
    model_instance = model_service(
        model=request.model_name or default_model_name,
        system_prompt=None,  # You might want to set this based on your needs
        temperature=0,
        chat_history=chat_history
    )
    
    # Create agent with the model instance
    agent = Agent(tools=tools, model_service=lambda **kwargs: model_instance, model_name=request.model_name, stop=stop)
    
    try:
        current_vars = load_variables()
        
        current_vars["lead_id"] = request.lead_id
        current_vars["dealer_id"] = request.dealers_id
        current_vars["lead_crm_id"] = request.lead_crm_id
        if request.product_id is not None:
            current_vars["product_id"] = request.product_id
        
        save_variables(current_vars)
        
        variables.dealer_id = request.dealers_id
        variables.lead_id = request.lead_id
        variables.lead_crm_id = request.lead_crm_id
        if request.product_id is not None:
            variables.product_id = request.product_id
        
        result = agent.work(request.prompt)
        
        save_chat_history(db, request.lead_id, request.prompt, result)
        
        return {
            "result": result,
            "dealers_id": variables.dealer_id,
            "lead_id": variables.lead_id,
            "lead_crm_id": variables.lead_crm_id,
            "product_id": variables.product_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)