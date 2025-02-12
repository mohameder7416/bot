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
from bot.toolbox.toolbox import ToolBox
from termcolor import colored
import json

class Agent:
    def __init__(self, tools, model_service, model_name=None, stop=None):
        self.tools = tools
        self.model_service = model_service
        self.model_name = model_name if model_name is not None else (
            "gpt-3.5-turbo" if model_service == OpenAIModel else None
        )
        self.stop = stop

    def prepare_tools(self):
        toolbox = ToolBox()
        toolbox.store(self.tools)
        tool_descriptions = toolbox.tools()
        return tool_descriptions

    def think(self, prompt):
        tool_descriptions = self.prepare_tools()
        agent_system_prompt = agent_system_prompt_template.format(
            tool_descriptions=tool_descriptions, dealer_prompt="start the conversation with (hello everyone and be funny)"
        )

        if self.model_service == OllamaModel:
            model_instance = self.model_service(
                model=self.model_name,
                system_prompt=agent_system_prompt,
                temperature=0,
                stop=self.stop
            )
        else:
            model_instance = self.model_service(
                model=self.model_name,
                system_prompt=agent_system_prompt,
                temperature=0
            )

        agent_response_dict = model_instance.generate_text(prompt)
        return agent_response_dict

    def work(self, prompt):
        agent_response_dict = self.think(prompt)
        
        tool_choice = agent_response_dict.get("tool_choice")
        tool_input = agent_response_dict.get("tool_input")
        
        tool_response = None
        for tool in self.tools:
            if tool.__name__ == tool_choice:
                tool_response = tool(tool_input)
                break

        if tool_response:
            complete_answer = self.generate_complete_answer(prompt, tool_choice, tool_input, tool_response)
        else:
            complete_answer = tool_input

        return complete_answer

    def generate_complete_answer(self, original_prompt, tool_choice, tool_input, tool_response):
        completion_prompt = f"""
        Original user query: {original_prompt}
        Tool used: {tool_choice}
        Tool input: {tool_input}
        Tool response: {tool_response}

        Based on the above information, provide a complete and helpful answer to the user's original query.
        Make sure to incorporate the tool's response into your answer.
        """

        model_instance = self.model_service(
            model=self.model_name,
            system_prompt="You are a helpful assistant providing complete answers based on tool responses.",
            temperature=0
        )

        complete_answer = model_instance.generate_text(completion_prompt)
        return complete_answer.get('tool_input', 'Sorry, I could not generate a complete answer.')

