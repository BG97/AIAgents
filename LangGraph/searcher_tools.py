from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from dotenv import load_dotenv
import os
import requests
from langchain.agents import Tool
from langchain.tools import StructuredTool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
import uuid
import sqlite3
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
    
load_dotenv(override=True)
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"
serper = GoogleSerperAPIWrapper()

class GetUserHistoryInput(BaseModel):
    username: str = Field(..., description="The username to fetch history for")
    query_text: str = Field(None, description="Natural language query about history to retrieve")

async def playwright_tools():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    return toolkit.get_tools(), browser, playwright


def push(text: str):
    """Send a push notification to the user"""
    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})
    return "success"


def get_file_tools():
    toolkit = FileManagementToolkit(root_dir="sandbox")
    return toolkit.get_tools()


def format_search_history(formatted_results, success_criteria=None):

    if not formatted_results:
        return "No search history found."
    
    
    prompt = f"""
    You are a formatting expert. Format the following search history data:
    
    {formatted_results}
    
    Format this data according to these requirements:
    {success_criteria if success_criteria else "Make it readable and well-organized."}
    
    Use plain text only (no HTML or Markdown). Return ONLY the formatted output without any explanation.
    You can use Unicode symbols, ASCII art, or emojis if appropriate.
    """

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    response = llm.invoke(prompt)
    return response.content
    
def get_user_history(query_text: str = None, username: str = None):
    """
    Retrieves search history from the database based on natural language query.
    Converts natural language to SQL, executes the query, and formats results.
    
    Args:
        username: The username to fetch history for (required)
        query_text: Natural language description of what history to retrieve (e.g. "show my searches about AI")
    """
    try:
        
        conn = sqlite3.connect("query_log.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_history'")
        if not cursor.fetchone():
            return "Error: The search history table does not exist yet. Try making some searches first."
        
        cursor.execute("PRAGMA table_info(search_history)")
        schema_info = cursor.fetchall()
        schema_description = "\n".join([f"- {col[1]} ({col[2]})" for col in schema_info])
        
        default_query = "SELECT * FROM search_history WHERE username = ? ORDER BY timestamp DESC"
        if query_text:
            llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)
            
            prompt = f"""
            Table name: search_history
            Table schema:
            {schema_description}
            
            User question: {query_text}
            Username filter: {username} (Always filter by this username for security)
            
            Generate a SQL query that answers the user's question while ALWAYS including 'WHERE username = ?' 
            in the query for security. Return ONLY the SQL query without explanation or backticks.
            """
            
            max_tries = 3
            sql_query = None
            
            for attempt in range(max_tries):
                try:
                    #print(f"Generating SQL (attempt {attempt+1}/{max_tries})...")
                    sql_response = llm.invoke(prompt)
                    generated_query = sql_response.content.strip()
                    
                    if "WHERE username = ?" not in generated_query and "where username = ?" not in generated_query:
                        generated_query = f"{generated_query} WHERE username = ?"
                    
                    #print(f"Generated query: {generated_query}")
                    
                    if generated_query.count("WHERE username = ?") > 1 or generated_query.count("where username = ?") > 1:
                        generated_query = generated_query.replace("WHERE username = ?", "").replace("where username = ?", "")
                        if "WHERE" not in generated_query and "where" not in generated_query:
                            generated_query = f"{generated_query} WHERE username = ?"
                        else:
                            generated_query = generated_query.replace("WHERE", "WHERE username = ? AND").replace("where", "where username = ? AND")
                    
                    conn.execute("EXPLAIN " + generated_query, (username,))
                    
                    sql_query = generated_query
                    break
                except Exception as e:
                    error_message = str(e)
                    print(f"SQL error on attempt {attempt+1}: {error_message}")
                    
                    prompt += f"\nPrevious attempt failed with error: {error_message}\nPlease fix and try again."
                    
                    if attempt == max_tries - 1:
                        print("Falling back to default query")
                        sql_query = default_query
        else:
            sql_query = default_query
        
        print(f"Executing query: {sql_query}")
        cursor.execute(sql_query, (username,))
        results = cursor.fetchall()
        
        formatted_results = []
        for row in results:
            record = {}
            for i, col in enumerate(cursor.description):
                record[col[0]] = row[i]
            formatted_results.append(record)
        
        conn.close()
        
        if not formatted_results:
            return "You don't have any search history records matching your query."
        
        output = "Here's your search history:\n\n"
        output += format_search_history(formatted_results)
        

        return output
        
    except Exception as e:
        print(f"[ERROR] Database error: {str(e)}")
        return f"Sorry, I encountered an error while retrieving your search history: {str(e)}"
        

async def other_tools():
    push_tool = Tool(name="send_push_notification", func=push, description="Use this tool when you want to send a push notification")
    file_tools = get_file_tools()

    tool_search =Tool(
        name="search",
        func=serper.run,
        description="Use this tool when you want to get the results of an online web search"
    )
    
    get_history_tool = StructuredTool(
                            name="get_user_history",
                            func=get_user_history,
                            description="""Use this tool when the user wants to view or query their search history.
                            
                            Examples of when to use this tool:
                            - User asks about their search history
                            - User wants to see previous searches
                            - User asks for specific searches (like "show my searches about AI")
                            
                            Required parameters:
                            - query_text: The user's natural language question about their history
                            - username: The username of the current user
                            """,
                            args_schema=GetUserHistoryInput
                        )
    wikipedia = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)

    python_repl = PythonREPLTool()
    
    return file_tools + [push_tool, tool_search, python_repl,  wiki_tool, get_history_tool]

