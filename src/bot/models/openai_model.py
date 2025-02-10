import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from dotenv import load_dotenv

load_dotenv()

class OpenAIModel:
    def __init__(self, model, system_prompt, temperature):
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
        """
        Creates a PromptTemplate with the given template and input variables.
        
        Args:
            template (str): The template string with variables in {variable} format
            input_variables (list): List of variable names used in the template
        
        Returns:
            PromptTemplate: The configured prompt template
        """
        return PromptTemplate(
            template=template,
            input_variables=input_variables
        )

    def generate_text(self, prompt, template=None, input_variables=None, **kwargs):
        """
        Generates text using either a raw prompt or a template with variables.
        
        Args:
            prompt (str): Either the raw prompt or the values for template variables
            template (str, optional): Template string if using PromptTemplate
            input_variables (list, optional): List of variable names if using template
            **kwargs: Additional keyword arguments for template variables
        
        Returns:
            tuple: (response_json, callback_info)
        """
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
            
            # Attempting to parse JSON response
            try:
                response_json = json.loads(response.content)
            except json.JSONDecodeError:
                print("Warning: Response is not in JSON format")
                response_json = {"content": response.content}
            
            # Create callback info dictionary
            callback_info = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": cb.total_cost
            }
            
           
            
            return response_json, callback_info