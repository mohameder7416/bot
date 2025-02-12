import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from dotenv import load_dotenv

load_dotenv()

class OpenAIModel:
    def __init__(self, model="gpt-3.5-turbo", system_prompt=None, temperature=0.7):
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
            
            try:
                # Attempt to parse the entire response content as JSON
                response_dict = json.loads(response.content)
                
                # Ensure the response has the expected keys
                if 'tool_choice' not in response_dict or 'tool_input' not in response_dict:
                    raise ValueError("Response does not contain expected keys")
                
                # If tool_input is a string, try to parse it as JSON
                if isinstance(response_dict['tool_input'], str):
                    try:
                        response_dict['tool_input'] = json.loads(response_dict['tool_input'])
                    except json.JSONDecodeError:
                        # If parsing fails, leave it as a string
                        pass
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Response parsing error - {str(e)}")
                response_dict = {
                    "tool_choice": "no tool",
                    "tool_input": response.content
                }
            
            print(f"\n\nResponse from OpenAI model: {response_dict}")
            
            return response_dict

