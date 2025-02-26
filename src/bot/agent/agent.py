import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from bot.prompts.prompts import agent_system_prompt_template
from bot.models.groq_model import GroqModel
from bot.models.openai_model import OpenAIModel
from bot.models.ollama_model import OllamaModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info
from bot.tools.make_appointment import make_appointment
from bot.toolbox.toolbox import ToolBox
from termcolor import colored
import json
import re 
import json
from termcolor import colored
from bot.utils.get_dealer_prompt import get_dealer_prompt
from bot.utils.chat_history import load_chat_history
from bot.utils.db import DataBase
from bot.utils.load_variables import load_variables
db = DataBase()

variables=load_variables()
lead_id=variables["lead_id"]
class Agent:
    def __init__(self, tools, model_service, model_name=None, stop=None):
        self.tools = tools
        self.model_service = model_service
        self.model_name = model_name if model_name is not None else (
            "gpt-4o" if model_service == OpenAIModel else None
        )
        self.stop = stop

    def prepare_tools(self):
        toolbox = ToolBox()
        toolbox.store(self.tools)
        tool_descriptions = toolbox.tools()
        # Enhance tool descriptions
        enhanced_descriptions = []
        for tool in tool_descriptions:
            if "get_dealers_info" in tool:
                enhanced_descriptions.append(f"{tool} Use this tool for queries about dealers, their locations, or dealer information.")
            elif "get_products_info" in tool:
                enhanced_descriptions.append(f"{tool} Use this tool for queries about products, their details, or product information.")
            elif "make_appointment" in tool:
                enhanced_descriptions.append(f"{tool} Use this tool for Generate a link to make an appointment between the customer and the dealer")    
            else:
                enhanced_descriptions.append(tool)
        return "\n".join(enhanced_descriptions)

    def think(self, prompt):
        tool_descriptions = self.prepare_tools()
        agent_system_prompt = agent_system_prompt_template.format(
            tool_descriptions=tool_descriptions, 
            dealer_prompt=get_dealer_prompt(),
            chat_history=load_chat_history(db,lead_id)
        )

        thinking_prompt = f"""
        User query: {prompt}

        Analyze this query carefully. If it relates to dealers or products or apppointement, you MUST use an appropriate tool.
        For dealer information, use get_dealers_info. For product information, use get_products_info. , for making a appointement use make_appointement
       
        Respond in the required JSON format with 'tool_choice' and 'tool_input'.
        """

        model_instance = self.model_service(
            model=self.model_name,
            system_prompt=agent_system_prompt,
            temperature=0
        )

        return model_instance.generate_text(thinking_prompt)

    def work(self, prompt):
        agent_response_dict = self.think(prompt)
        
        tool_choice = agent_response_dict.get("tool_choice")
        tool_input = agent_response_dict.get("tool_input")
        
        print(f"Debug - Tool chosen: {tool_choice}")
        print(f"Debug - Tool input: {tool_input}")
        
        tool_response = None
        if tool_choice != "no tool":
         for tool in self.tools:
            if tool.__name__ == tool_choice:
                if tool.__name__ == "make_appointment":
                    # Call make_appointment without arguments
                    tool_response = tool()
                elif isinstance(tool_input, dict):
                    if 'args' in tool_input:
                        tool_response = tool(**tool_input['args'])
                    elif 'kwargs' in tool_input:
                        tool_response = tool(**tool_input['kwargs'])
                    else:
                        tool_response = tool(**tool_input)
                else:
                    tool_response = tool(tool_input)
                break

        if tool_response:
            print(f"Debug - Tool response: {tool_response}")
            return self.generate_complete_answer(prompt, tool_choice, tool_input, tool_response)
        else:
            return agent_response_dict.get('tool_input', "I'm sorry, I couldn't process that request.")

      

    def generate_complete_answer(self, original_prompt, tool_choice, tool_input, tool_response):
        completion_prompt = f"""
        Original user query: {original_prompt}
        Tool used: {tool_choice}
        Tool input: {tool_input}
        Tool response: {tool_response}

        Based on the above information, provide a complete and helpful answer to the user's original query.
        Make sure to incorporate the tool's response into your answer if a tool was used.
        If no tool was used, provide a direct response to the query.
        """
        print("complete_prompt", completion_prompt)
        model_instance = self.model_service(
            model=self.model_name,
            system_prompt="You are a helpful assistant providing complete answers based on tool responses.",
            temperature=0
        )

        complete_answer = model_instance.generate_text(completion_prompt)
        if isinstance(complete_answer, dict):
            return complete_answer.get('tool_input', 'Sorry, I could not generate a complete answer.')
        return complete_answer

    def run(self):
        print(colored("Welcome to the Agent! Type 'exit' to quit.", 'green'))
        while True:
            prompt = input(colored("Ask me anything: ", 'cyan'))
            if prompt.lower() == "exit":
                break
            
            answer = self.work(prompt)
            print(colored(f"Agent: {answer}", 'yellow'))

if __name__ == "__main__":
    tools = [get_products_info, get_dealers_info,make_appointment]
    model_service = OllamaModel
    model_name = 'phi4'
    stop = None

    agent = Agent(tools=tools, model_service=model_service, model_name=model_name, stop=stop)
    agent.run()