from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List, Any, Optional, Dict
from pydantic import BaseModel, Field
from searcher_tools import playwright_tools, other_tools
import uuid
import asyncio
from datetime import datetime
import sqlite3
import json
load_dotenv(override=True)

class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    username: str
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool
    tool_name: Optional[str] 
    #query_text: Optional[str]

class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met")
    user_input_needed: bool = Field(description="True if more input is needed from the user, or clarifications, or the assistant is stuck")


class Search:
    def __init__(self):
        self.worker_llm_with_tools = None
        self.evaluator_llm_with_output = None
        self.tools = None
        self.llm_with_tools = None
        self.graph = None
        self.search_id = str(uuid.uuid4())
        self.memory = MemorySaver()
        self.browser = None
        self.playwright = None
        self.formatting_llm = None
    async def setup(self):
        self.tools, self.browser, self.playwright = await playwright_tools()
        self.tools += await other_tools()
        worker_llm = ChatOpenAI(model="gpt-4o-mini")
        self.worker_llm_with_tools = worker_llm.bind_tools(self.tools)
        evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
        self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        self.formatting_llm = ChatOpenAI(model="gpt-4o-mini")
        await self.build_graph()

    def worker(self, state: State) -> Dict[str, Any]:

        if not state.get("username") or state["username"].strip() == "":
            # Username not provided, return response asking for username
            response = AIMessage(content="Please provide a username before search or accessing search history.")
            new_state = dict(state)
            new_state["messages"] = [response]
            new_state["tool_name"] = None
            new_state["user_input_needed"] = True  # Signal that we need user input
            return new_state

        system_message = f"""You are a helpful assistant that can use tools to complete tasks.
                            You keep working on a task until either you have a question or clarification for the user, or the success criteria is met.

                            You have many tools to help you, including tools to query the user's search history, browse the internet, navigating and retrieving web pages.
                            You have a tool to run python code, but note that you would need to include a print() statement if you wanted to receive output.

                            The username is {state["username"]}    The current date and time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

                            This is the success criteria:
                            {state['success_criteria']}

                            IMPORTANT GUIDELINE:
                            - When the user asks about their search history (like entries, timestamps, or other database queries), simply pass their request to the get_user_history tool.
                            - DO NOT break down a single history request into multiple separate tool calls.
                            - Let the specialized tools handle the interpretation of natural language queries into database operations.

                            You should reply either with a question for the user about this assignment, or with your final response.
                            If you have a question for the user, you need to reply by clearly stating your question. An example might be:

                            Question: please clarify whether you want a summary or a detailed answer

                            If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer.
                            """
                    
        if state.get("feedback_on_work"):
            system_message += f"""
                Previously you thought you completed the assignment, but your reply was rejected because the success criteria was not met.
                Here is the feedback on why this was rejected:
                {state['feedback_on_work']}
                With this feedback, please continue the assignment, ensuring that you meet the success criteria or have a question for the user."""
        
        # Add in the system message

        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True
        
        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages
        
        # Invoke the LLM with tools
        response = self.worker_llm_with_tools.invoke(messages)
        tool_name = None
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_name = response.tool_calls[0]["name"]
            print(f"Next tool to run: {tool_name}")
        # Return updated state
        new_state = dict(state)  
        new_state["messages"] = [response]  
        new_state["tool_name"] = tool_name  
        
        return new_state


    def worker_router(self, state: State) -> str:
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"
        
        
    def format_conversation(self, messages: List[Any]) -> str:
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tools use]"
                conversation += f"Assistant: {text}\n"
        return conversation
        
    def evaluator(self, state: State) -> State:
        last_response = state["messages"][-1].content

        system_message = f"""You are an evaluator that determines if a task has been completed successfully by an Assistant.
            Assess the Assistant's last response based on the given criteria. Respond with your feedback, and with your decision on whether the success criteria has been met,
            and whether more input is needed from the user."""

        user_message = f"""You are evaluating a conversation between the User and Assistant. You decide what action to take based on the last response from the Assistant.

            The entire conversation with the assistant, with the user's original request and all replies, is:
            {self.format_conversation(state['messages'])}

            The success criteria for this assignment is:
            {state['success_criteria']}

            And the final response from the Assistant that you are evaluating is:
            {last_response}

            Respond with your feedback, and decide if the success criteria is met by this response.
            Also, decide if more user input is required, either because the assistant has a question, needs clarification, or seems to be stuck and unable to answer without help.

            The Assistant has access to tools, including a tool to retrieve search history. If the Assistant correctly uses this tool, regardless of the result (which depends on permissions),
            then consider the success criteria met if the Assistant did its job correctly and communicated results or limitations properly.
            """
        if state["feedback_on_work"]:
            user_message += f"Also, note that in a prior attempt from the Assistant, you provided this feedback: {state['feedback_on_work']}\n"
            user_message += "If you're seeing the Assistant repeating the same mistakes, then consider responding that user input is required."
        
        evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        eval_result = self.evaluator_llm_with_output.invoke(evaluator_messages)
        new_state = {
            "messages": [{"role": "assistant", "content": f"Evaluator Feedback on this answer: {eval_result.feedback}"}],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed
        }
        return new_state

    def route_based_on_evaluation(self, state: State) -> str:
        is_admin = state['username'] == 'admin'

        if state["success_criteria_met"] or state["user_input_needed"]:
            # Log search for non-admin users immediately
            if not is_admin:
                self.log_search(
                    state['username'],
                    self.search_id,
                    state['feedback_on_work'],
                    state["messages"][-2].content
                )
            print(state["messages"])
            return "format_final_output"
        else:
            return "worker"

   
    
    def route_based_on_tools(self, state: State) -> str:
        last_message = state["messages"][-1]
        print("Tool output:", last_message.content)
        
        tool_name = state.get("tool_name")
        print("Tool name detected:", tool_name)
        
        if tool_name == "get_user_history":
            if not state.get("username") or state["username"].strip() == "":

                # Add a message to state explaining why access is denied
                state["messages"].append(AIMessage(content="Error: Username is required to access search history. Please provide a username."))
                return "END"  # End the flow with error message
            
            print("Detected get_user_history tool, routing to END")
            return "END"
        else:
            print("Routing to worker")
            return "worker"
    


    def log_search(self,username:str,thread_id: str, feedback: str, reply: str):
        conn = sqlite3.connect("query_log.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO search_history (thread_id, username,  feedback, reply)
            VALUES (?, ?, ?, ?)
        ''', (thread_id,username, feedback, reply))
        conn.commit()
        conn.close()

    def format_final_output(self,state: State) -> Dict[str, Any]:

            
        messages = state["messages"]
        new_messages = []
        
        for msg in reversed(messages):
            if (isinstance(msg, AIMessage) and 
                not msg.content.startswith("Evaluator Feedback")):
                new_messages = [msg]  
                break
        

        new_state = dict(state)
        new_state["messages"] = new_messages
        return new_state
    

    async def build_graph(self):
        # Set up Graph Builder with State
        graph_builder = StateGraph(State)

        # Add nodes
        graph_builder.add_node("worker", self.worker)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_node("evaluator", self.evaluator)
        graph_builder.add_node("format_final_output", self.format_final_output)

        # Add edges
        graph_builder.add_conditional_edges("worker", self.worker_router, {"tools": "tools", "evaluator": "evaluator"})
        graph_builder.add_conditional_edges("tools", self.route_based_on_tools, {"worker": "worker", "END": END})
        graph_builder.add_conditional_edges("evaluator", self.route_based_on_evaluation, {"worker": "worker", "format_final_output": 'format_final_output'})
        graph_builder.add_edge("format_final_output",END)
        graph_builder.add_edge(START, "worker")

        # Compile the graph
        self.graph = graph_builder.compile(checkpointer=self.memory)

    async def run_superstep(self, message, username, success_criteria, history):
        config = {"configurable": {"thread_id": self.search_id}}

        state = {
            "messages": message,
            "username": username,
            "success_criteria": success_criteria or "The answer should be clear and accurate",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False,
            "tool_name": None
        }
        result = await self.graph.ainvoke(state, config=config)



        user = {"role": "user", "content": message}
        reply = {"role": "assistant", "content": result["messages"][-2].content}
        feedback = {"role": "assistant", "content": result["messages"][-1].content}
        

        return history + [user, reply, feedback]
    





    def cleanup(self):
        if self.browser:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.browser.close())
                if self.playwright:
                    loop.create_task(self.playwright.stop())
            except RuntimeError:
                # If no loop is running, do a direct run
                asyncio.run(self.browser.close())
                if self.playwright:
                    asyncio.run(self.playwright.stop())
