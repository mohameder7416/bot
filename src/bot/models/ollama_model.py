


from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import json

class OllamaModel:
    def __init__(self, model, system_prompt, temperature=0.8, stop=None):
        """
        Initializes the OllamaModel with the given parameters using LangChain.
        
        Parameters:
        model (str): The name of the model to use.
        system_prompt (str): The system prompt to use.
        temperature (float): The temperature setting for the model.
        stop (str): The stop token for the model.
        """
        self.model = Ollama(
            model=model,
            temperature=temperature,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            stop=stop
        )
        self.system_prompt = system_prompt
        self.prompt_template = PromptTemplate(
            input_variables=["system_prompt", "user_prompt"],
            template="{system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
        )
        self.chain = LLMChain(llm=self.model, prompt=self.prompt_template)
    
    def generate_text(self, prompt):
        """
        Generates a response from the Ollama model based on the provided prompt using LangChain.
        
        Parameters:
        prompt (str): The user query to generate a response for.
        
        Returns:
        dict: The response from the model as a dictionary.
        """
        try:
            response = self.chain.run(system_prompt=self.system_prompt, user_prompt=prompt)
            
            print(f"\n\nResponse from Ollama model: {response}")
            
            # Attempt to parse the response as JSON
            try:
                response_dict = json.loads(response)
            except json.JSONDecodeError:
                # If parsing fails, wrap the response in a dictionary
                response_dict = {"response": response}
            
            return response_dict
        except Exception as e:
            response = {"error": f"Error in invoking model! {str(e)}"}
            return response