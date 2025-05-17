from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from dotenv import load_dotenv
import os
import requests
from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
import uuid
import sqlite3
load_dotenv(override=True)
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"
serper = GoogleSerperAPIWrapper()

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




def get_user_history(username: str):
    """
    Retrieves search history from the database for the given username only.
    Users can only view their own search records.
    """
    try:
        conn = sqlite3.connect("query_log.db")
        cursor = conn.cursor()

        # Ensure table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_history'")
        if not cursor.fetchone():
            print("[ERROR] search_history table does not exist")
            return []

        # Query the user's own records
        query = '''
        SELECT * FROM search_history
        WHERE username = ?
        ORDER BY timestamp DESC 
        '''
        cursor.execute(query, (username,))
        results = cursor.fetchall()

        # Format the results into dictionaries
        formatted_results = []
        for row in results:
            record = {}
            for i, col in enumerate(cursor.description):
                record[col[0]] = row[i]
            formatted_results.append(record)

        conn.close()
        return formatted_results

    except Exception as e:
        print(f"[ERROR] Database error: {str(e)}")
        return []

async def other_tools():
    push_tool = Tool(name="send_push_notification", func=push, description="Use this tool when you want to send a push notification")
    file_tools = get_file_tools()

    tool_search =Tool(
        name="search",
        func=serper.run,
        description="Use this tool when you want to get the results of an online web search"
    )
    
    get_history_tool = Tool(
                            name="get_user_history",
                            func=get_user_history,
                            description="Use this tool when user wants to view their own search history"
                        )
    wikipedia = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)

    python_repl = PythonREPLTool()
    
    return file_tools + [push_tool, tool_search, python_repl,  wiki_tool, get_history_tool]

