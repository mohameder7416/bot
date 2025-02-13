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

# Load environment variables
load_dotenv()

app = FastAPI()

# Database setup
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SelectedItem(Base):
    __tablename__ = "selected_item"

    id = Column(Integer, primary_key=True, index=True)
    dealers_id = Column(Integer, index=True)  # Changed to Integer

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AgentRequest(BaseModel):
    prompt: str
    model_service: str
    model_name: Optional[str] = None
    dealers_id: int  # Changed to int

@app.post("/agent")
async def run_agent(request: AgentRequest, db: Session = Depends(get_db)):
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
        
        # Check if a record with the given dealers_id already exists
        existing_item = db.query(SelectedItem).filter(SelectedItem.dealers_id == request.dealers_id).first()
        
        if existing_item:
            # Update the existing record
            existing_item.dealers_id = request.dealers_id
            db.commit()
        else:
            # Add a new record
            new_item = SelectedItem(dealers_id=request.dealers_id)
            db.add(new_item)
            db.commit()
        
        return {"result": result, "dealers_id": request.dealers_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))