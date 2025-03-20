import json
import os
import re
import asyncio
from typing import Optional, Callable, Dict, Any, AsyncGenerator, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv

load_dotenv()

class QueueCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""
    
    def __init__(self, queue):
        self.queue = queue
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.queue.put_nowait(token)

class OpenAIModel:
    def __init__(self, model="gpt-4o", system_prompt=None, temperature=0.7):
        self.temperature = temperature
        self.model = model
        self.system_prompt = system_prompt
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        # Non-streaming chat for regular responses
        self.chat = ChatOpenAI(
            model_name=self.model,
            temperature=self.temperature,
            openai_api_key=self.api_key
        )

    def create_prompt_template(self, template, input_variables):
        return PromptTemplate(
            template=template,
            input_variables=input_variables
        )

    def generate_text(self, prompt, template=None, input_variables=None, **kwargs):
        if template and input_variables:
            prompt_template = self.create_prompt_template(template, input_variables)
            final_prompt = prompt_template.format(**kwargs)
        else:
            final_prompt = prompt

        messages = [
            SystemMessage(content=self.system_prompt) if self.system_prompt else None,
            HumanMessage(content=final_prompt)
        ]
        messages = [m for m in messages if m is not None]
        
        with get_openai_callback() as cb:
            response = self.chat.invoke(messages)
            
            # Try to extract JSON from the response content
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # If no JSON found in code block, try to parse the entire content
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return {"tool_choice": "no tool", "tool_input": response.content}
    
    async def agenerate_text(self, prompt, template=None, input_variables=None, **kwargs):
        """Generate text asynchronously"""
        if template and input_variables:
            prompt_template = self.create_prompt_template(template, input_variables)
            final_prompt = prompt_template.format(**kwargs)
        else:
            final_prompt = prompt

        messages = [
            SystemMessage(content=self.system_prompt) if self.system_prompt else None,
            HumanMessage(content=final_prompt)
        ]
        messages = [m for m in messages if m is not None]
        
        response = await self.chat.ainvoke(messages)
        
        # Try to extract JSON from the response content
        json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # If no JSON found in code block, try to parse the entire content
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"tool_choice": "no tool", "tool_input": response.content}
    
    def get_streaming_chat(self, callbacks=None):
        """Get a streaming chat model with callbacks"""
        return ChatOpenAI(
            model_name=self.model,
            temperature=self.temperature,
            openai_api_key=self.api_key,
            streaming=True,
            callbacks=callbacks
        )