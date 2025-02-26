import json
import os
import re
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LangTrace for tracking
try:
    from langtrace_python_sdk import langtrace
    langtrace.init()
except ImportError:
    print("LangTrace SDK not found. Continuing without tracing.")

class OllamaModel:
    def __init__(self, model, system_prompt=None, temperature=0.7, stop=None, base_url="http://localhost:11434"):
        """
        Initializes the OllamaModel with the given parameters using LangChain.
        
        Parameters:
            model (str): The name of the model to use.
            system_prompt (str): The system prompt to use.
            temperature (float): The temperature setting for the model.
            stop (list or str): The stop tokens for the model.
            base_url (str): The API endpoint for the locally installed Ollama instance.
        """
        self.model_name = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.base_url = base_url
        
        self.llm = OllamaLLM(
            model=self.model_name,
            temperature=self.temperature,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            stop=stop,
            base_url=self.base_url
        )
    
    def create_prompt_template(self, template, input_variables):
        """
        Creates a prompt template with the given template and input variables.
        
        Parameters:
            template (str): The template string.
            input_variables (list): The list of input variables.
            
        Returns:
            PromptTemplate: The created prompt template.
        """
        return PromptTemplate(
            template=template,
            input_variables=input_variables
        )
    
    def generate_text(self, prompt, template=None, input_variables=None, **kwargs):
        """
        Generates text using the Ollama model, mimicking the OpenAI interface.
        
        Parameters:
            prompt (str): The user prompt.
            template (str, optional): A template string for formatting the prompt.
            input_variables (list, optional): Input variables for the template.
            **kwargs: Additional keyword arguments for template formatting.
            
        Returns:
            dict: Response in a format similar to OpenAI's output.
        """
        try:
            # Format the final prompt based on template if provided
            if template and input_variables:
                prompt_template = self.create_prompt_template(template, input_variables)
                final_prompt = prompt_template.format(**kwargs)
            else:
                final_prompt = prompt
            
            # Create the chain with system prompt and user prompt
            system_message = self.system_prompt or "You are a helpful assistant."
            full_prompt_template = PromptTemplate(
                input_variables=["system_prompt", "user_prompt"],
                template="{system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
            )
            
            chain = LLMChain(llm=self.llm, prompt=full_prompt_template)
            
            # Run the chain
            response = chain.run(system_prompt=system_message, user_prompt=final_prompt)
            
            print(f"\n\nResponse from Ollama model: {response}")
            
            # Try to extract JSON from the response content
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # If no JSON found in code block, try to parse the entire content
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                print(f"Warning: Unable to parse response as JSON: {response}")
                return {"tool_choice": "no tool", "tool_input": response}
                
        except Exception as e:
            error_message = f"Error generating text: {str(e)}"
            print(error_message)
            return {"error": error_message}