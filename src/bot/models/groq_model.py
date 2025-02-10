import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import json

class GroqModel:
    def __init__(self, model, system_prompt, temperature=0):  # Removed stop parameter
        """
        Initializes the GroqModel with the given parameters using LangChain.
        
        Parameters:
        model (str): The name of the model to use (e.g., 'llama-3.1-405b-reasoning').
        system_prompt (str): The system prompt to use.
        temperature (float): The temperature setting for the model.
        """
        if "GROQ_API_KEY" not in os.environ:
            raise ValueError("GROQ_API_KEY must be set in the environment")
        
        self.model = ChatGroq(
            model_name=model,
            temperature=temperature,
            groq_api_key=os.environ["GROQ_API_KEY"],
            callbacks=[StreamingStdOutCallbackHandler()]
            # Removed stop parameter here
        )
        self.system_prompt = system_prompt
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}")
        ])
        self.chain = self.prompt_template | self.model
    
    def generate_text(self, prompt):
        """
        Generates a response from the Groq model based on the provided prompt using LangChain.
        
        Parameters:
        prompt (str): The user query to generate a response for.
        
        Returns:
        dict: The response from the model as a dictionary.
        """
        try:
            response = self.chain.invoke({
                "system_prompt": self.system_prompt,
                "user_prompt": prompt
            })
            
            print(f"\n\nFull Response from Groq model: {response.content}")
            
            # Wrap the response in a dictionary
            response_dict = {"response": response.content}
            
            return response_dict
        except Exception as e:
            response = {"error": f"Error in invoking model! {str(e)}"}
            return response