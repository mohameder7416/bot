import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from dotenv import load_dotenv
import re
load_dotenv()
# Must precede any llm module imports

from langtrace_python_sdk import langtrace

langtrace.init()
class OpenAIModel:
    def __init__(self, model="gpt-4o", system_prompt=None, temperature=0.7):
        self.temperature = temperature
        self.model = model
        self.system_prompt = system_prompt
        self.api_key = os.getenv('OPENAI_API_KEY')
        
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
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=final_prompt)
        ]
        
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
                print(f"Warning: Unable to parse response as JSON: {response.content}")
                return {"tool_choice": "no tool", "tool_input": response.content}