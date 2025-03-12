import sys
from pathlib import Path
import json
import os
import re

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from bot.prompts.prompts import agent_system_prompt_template
from bot.models.openai_model import OpenAIModel
from bot.tools.get_dealers_info import get_dealers_info
from bot.tools.get_products_info import get_products_info
from bot.tools.make_appointment import make_appointment
from bot.toolbox.toolbox import ToolBox
from bot.utils.get_dealer_prompt import get_dealer_prompt
from bot.utils.chat_history import load_chat_history
from bot.utils.db import DataBase
from bot.utils.load_variables import load_variables
from termcolor import colored
# Environment variables
PWA_DB_HOST_V12CHAT_READ = os.getenv("PWA_DB_HOST_V12CHAT_READ")
PWA_DB_USERNAME_V12CHAT_READ = os.getenv("PWA_DB_USERNAME_V12CHAT_READ")
PWA_DB_PASSWORD_V12CHAT_READ = os.getenv("PWA_DB_PASSWORD_V12CHAT_READ")
PWA_DB_DATABASE_V12CHAT_READ = os.getenv("PWA_DB_DATABASE_V12CHAT_READ")
db = DataBase(
    host=PWA_DB_HOST_V12CHAT_READ,
    user=PWA_DB_USERNAME_V12CHAT_READ,
    password=PWA_DB_PASSWORD_V12CHAT_READ,
    database=PWA_DB_DATABASE_V12CHAT_READ,
    port=3306
)

variables = load_variables()
lead_id = variables["lead_id"]

class Agent:
    def __init__(self, tools, model_service, model_name=None, stop=None):
        self.tools = tools
        self.model_service = model_service
        self.model_name = model_name if model_name is not None else (
            "gpt-4o" if model_service == OpenAIModel else None
        )
        self.stop = stop
        self.tools_dict = {tool.__name__: tool for tool in tools}

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

    def think(self, prompt, previous_tools_data=None):
        """
        Enhanced thinking step that can consider previous tool outputs
        """
        tool_descriptions = self.prepare_tools()
        agent_system_prompt = agent_system_prompt_template.format(
            tool_descriptions=tool_descriptions, 
            dealer_prompt=get_dealer_prompt(),
            chat_history=load_chat_history(db, lead_id)
        )

        thinking_prompt = f"""
        User query: {prompt}

        Analyze this query carefully. If it relates to dealers or products or appointment, you MUST use an appropriate tool.
        For dealer information, use get_dealers_info. For product information, use get_products_info. For making an appointment use make_appointment.
        
        You can use multiple tools if needed to fully answer the query.
        """
        
        # Add previous tool data if available
        if previous_tools_data:
            thinking_prompt += f"\n\nPrevious tool executions:\n{json.dumps(previous_tools_data, indent=2)}\n\n"
            thinking_prompt += "Based on these previous tool results, determine if you need additional tools or can now provide a final answer."
        
        thinking_prompt += """
        Respond in the required JSON format with:
        - 'tool_choice': The tool to use next (or "no tool" if ready to provide final answer)
        - 'tool_input': The input for the chosen tool
        - 'needs_more_tools': true/false indicating if you'll need more tools after this one
        - 'reasoning': Brief explanation of why you chose this tool and what you hope to learn
        """

        model_instance = self.model_service(
            model=self.model_name,
            system_prompt=agent_system_prompt,
            temperature=0
        )

        response = model_instance.generate_text(thinking_prompt)
        
        # Ensure we have a proper JSON response
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                # Try to extract JSON from the string
                json_match = re.search(r'({.*})', response.replace('\n', ''), re.DOTALL)
                if json_match:
                    try:
                        response = json.loads(json_match.group(1))
                    except:
                        response = {
                            "tool_choice": "no tool",
                            "tool_input": response,
                            "needs_more_tools": False,
                            "reasoning": "Failed to parse JSON response"
                        }
                else:
                    response = {
                        "tool_choice": "no tool",
                        "tool_input": response,
                        "needs_more_tools": False,
                        "reasoning": "Failed to parse JSON response"
                    }
        
        return response

    def execute_tool(self, tool_choice, tool_input):
        """
        Execute a single tool and return its response
        """
        if tool_choice not in self.tools_dict:
            return f"Error: Tool '{tool_choice}' not found"
            
        tool = self.tools_dict[tool_choice]
        
        try:
            if tool_choice == "make_appointment":
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
                
            return tool_response
        except Exception as e:
            return f"Error executing tool {tool_choice}: {str(e)}"

    def analyze_tool_output(self, original_prompt, tool_choice, tool_input, tool_response, previous_tools_data=None):
        """
        Analyze the output of a tool to extract insights
        """
        analysis_prompt = f"""
        Original user query: {original_prompt}
        Tool used: {tool_choice}
        Tool input: {json.dumps(tool_input, indent=2)}
        Tool response: {json.dumps(tool_response, indent=2) if isinstance(tool_response, (dict, list)) else tool_response}
        
        Analyze this tool response carefully. Extract the key information and insights from it.
        What are the most important facts or details from this response that help answer the user's query?
        Are there any limitations or gaps in this information that might require using additional tools?
        """
        
        if previous_tools_data:
            analysis_prompt += f"\n\nPrevious tool executions:\n{json.dumps(previous_tools_data, indent=2)}"
        
        model_instance = self.model_service(
            model=self.model_name,
            system_prompt="You are an analytical assistant that extracts key insights from tool outputs.",
            temperature=0
        )

        analysis = model_instance.generate_text(analysis_prompt)
        
        return analysis

    def work(self, prompt):
        """
        Enhanced work method that can use multiple tools sequentially
        """
        tools_data = []  # Store data from all tool executions
        max_tool_calls = 4  # Prevent infinite loops
        
        # First thinking step
        agent_response = self.think(prompt)
        
        tool_choice = agent_response.get("tool_choice")
        tool_input = agent_response.get("tool_input")
        needs_more_tools = agent_response.get("needs_more_tools", False)
        reasoning = agent_response.get("reasoning", "")
        
        tool_call_count = 0
        
        while tool_choice != "no tool" and tool_call_count < max_tool_calls:
            print(f"Debug - Tool chosen: {tool_choice}")
            print(f"Debug - Tool input: {tool_input}")
            print(f"Debug - Reasoning: {reasoning}")
            
            # Execute the tool
            tool_response = self.execute_tool(tool_choice, tool_input)
            print(f"Debug - Tool response: {tool_response}")
            
            # Analyze the tool output
            analysis = self.analyze_tool_output(prompt, tool_choice, tool_input, tool_response, tools_data if tools_data else None)
            print(f"Debug - Analysis: {analysis}")
            
            # Store this tool execution data
            tools_data.append({
                "tool": tool_choice,
                "input": tool_input,
                "response": tool_response,
                "analysis": analysis,
                "reasoning": reasoning
            })
            
            tool_call_count += 1
            
            # If we don't need more tools or reached the limit, break
            if not needs_more_tools or tool_call_count >= max_tool_calls:
                break
                
            # Think again with the accumulated tool data
            agent_response = self.think(prompt, tools_data)
            
            tool_choice = agent_response.get("tool_choice")
            tool_input = agent_response.get("tool_input")
            needs_more_tools = agent_response.get("needs_more_tools", False)
            reasoning = agent_response.get("reasoning", "")
        
        # Generate the final answer
        return self.generate_complete_answer(prompt, tools_data)

    def generate_complete_answer(self, original_prompt, tools_data):
        """
        Generate a complete answer based on all tool executions
        """
        if not tools_data:
            # No tools were used, provide direct response
            model_instance = self.model_service(
                model=self.model_name,
                system_prompt="You are a helpful dealership assistant providing direct answers.",
                temperature=0
            )
            return model_instance.generate_text(original_prompt)
        
        # Format all tool data for the completion prompt
        tools_summary = ""
        for i, data in enumerate(tools_data):
            tools_summary += f"Tool {i+1}: {data['tool']}\n"
            tools_summary += f"Input: {json.dumps(data['input'], indent=2)}\n"
            tools_summary += f"Response: {json.dumps(data['response'], indent=2) if isinstance(data['response'], (dict, list)) else data['response']}\n"
            tools_summary += f"Analysis: {data['analysis']}\n\n"
        
        completion_prompt = f"""
        Original user query: {original_prompt}
        
        Tool executions and analyses:
        {tools_summary}
        
        Based on all the above information, provide a complete, helpful, and persuasive answer to the user's original query.
        Integrate insights from all tools used to create a comprehensive response.
        Remember you are a dealership assistant trying to convince the customer to purchase products and book an appointment.
        Use the same language the user provided in their query.
        Be concise and direct in your response.
        """
        
        model_instance = self.model_service(
            model=self.model_name,
            system_prompt="You are a helpful dealership assistant providing complete answers based on tool responses.",
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
    model_service = OpenAIModel
    model_name = 'gpt-3.5-turbo'
    stop = None

    agent = Agent(tools=tools, model_service=model_service, stop=stop)
    agent.run()            