---
title: SearchOps_Assistant
app_file: app.py
sdk: gradio
sdk_version: 5.29.1
---

# Search Personal Co-Worker

An intelligent search assistant built on LangGraph that can answer questions, perform web searches, record query history, and support personalized interactions.

## Project Overview

This project creates a smart search agent capable of finding information, answering questions, and maintaining search history records. Built using the LangGraph framework, it combines various tools to provide a rich search experience.

## Key Features

- **Intelligent Search**: Answer complex questions like "Where to find the best Chinese food in New York" or "What are the strongest AI technologies in 2025"
- **Search History Management**: Automatically saves all search records, allowing users to query their history using natural language (e.g., "give me all the search history")
- **Multi-Tool Integration**: Combines web search, Wikipedia, Python computation and other tools to provide comprehensive answers
- **Personalized Experience**: Recognizes users by username and saves individual search histories
- **Evaluation Mechanism**: Supports custom success criteria to evaluate search result quality
- **Automated Execution**: Uses Docker for automated program running and web scraping capabilities
- **Mobile Notifications**: Integrates with Pushover API to send real-time notifications to mobile devices
- **Web Scraping**: Employs Pydantic for structured data extraction from websites

## Project Structure

The project consists of three main files:

- **app.py**: Frontend interface responsible for user interaction
- **search.py**: LangGraph core backend that manages the search process and graph nodes
- **search_tools.py**: Defines all tools and agent functionalities

## LangGraph Architecture

The search flow consists of the following nodes:

- **StartNode**: Initializes the search process
- **WorkerNode**: Handles the main search logic
- **ToolsNode**: Manages and executes various external tools
- **EvaluatorNode**: Evaluates whether search results meet success criteria
- **SQLFormatterNode**: Processes database-related queries
- **EndNode**: Completes the search process and returns results

## Integrated Tools

This project integrates several powerful tools:

1. **Search Tool**: Online web search functionality
2. **History Query Tool**: Retrieves user's past search history
3. **Wikipedia Tool**: Directly queries Wikipedia content
4. **Python REPL**: Executes Python code for calculations or data processing
5. **Push Notification Tool**: Sends push notifications to mobile devices via Pushover API
6. **File Tools**: File read/write operations
7. **Docker Execution**: Securely runs code in isolated containers
8. **Web Scraping**: Uses Pydantic models for structured web data extraction

## Installation & Setup

### Requirements

- Python 3.8+
- Docker (for automated program execution)
- Required dependencies (see requirements.txt)
- Pushover account and API key (for mobile notifications)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd [project-folder]
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Set up environment variables:
   ```bash
   # Required for Pushover notifications
   export PUSHOVER_USER_KEY=your_user_key
   export PUSHOVER_API_TOKEN=your_api_token
   ```

4. Install Docker (if not already installed):
   ```bash
   # For Ubuntu
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io
   
   # For macOS and Windows, download and install Docker Desktop
   ```

### Running the Application

```bash
python app.py
```

The application will start locally. Access the URL displayed in the terminal (typically http://localhost:7860) to use the search assistant.

## Usage Guide

1. Enter your username (used to record search history)
2. Type your question in the search box
3. Specify success criteria (optional, used to evaluate result quality)
4. Click the "Search" button
5. View your search results
6. Query your history by entering commands like "give me all the search history"
7. Receive push notifications on your mobile device for important alerts

## Deploying to Hugging Face

To deploy this project to Hugging Face Spaces:

1. Create a setup.sh file with the following content:
   ```bash
   #!/bin/bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Create a .hf directory with a requirements.txt file containing:
   ```
   execute_setup_sh==True
   ```

3. Set up repository secrets in Hugging Face for sensitive API keys:
   - PUSHOVER_USER_KEY
   - PUSHOVER_API_TOKEN

4. Ensure your code runs in headless mode for Playwright:
   ```python
   browser = playwright.chromium.launch(headless=True)
   ```

5. Note: Docker execution features may have limited functionality in the Hugging Face environment

## Troubleshooting

If you encounter issues during deployment, check:
- Browser binary installation (Playwright requires additional setup)
- Environment differences between local and deployment
- Path configurations and dependencies
- API key configuration for Pushover notifications
- Docker availability and permissions in your deployment environment

## Contributing

Contributions to improve the project are welcome. Please feel free to submit a pull request or open an issue.

## License

Benny

