# 🧠 DeepResearch: Autonomous Research Assistant

**DeepResearch** is an autonomous research agent powered by OpenAI Assistants and Gradio. Simply enter a research topic, and the system will:

- ✍️ Automatically plan a search strategy  
- 🔍 Perform web searches in parallel  
- 📚 Summarize the results into a structured report  
- 📧 (Optional) Email the report using SendGrid  

👉 [Try it live on Hugging Face](https://huggingface.co/spaces/Benny97/DeepResearch)

## 🔧 Features

- **Planner Agent**: Plans search steps based on the input query  
- **Search Agent**: Executes multi-threaded web search using OpenAI tools  
- **Writer Agent**: Summarizes search results into a clean markdown report  
- **Email Agent**: Sends the report via SendGrid (optional)  
- **Research Manager**: Orchestrates the workflow asynchronously using `asyncio`  

## 🗂️ Project Structure

DeepResearch/
├── deep_research.py # Main app entry (Gradio)
├── research_manager.py # Manages all agents and logic
├── planner_agent.py # Defines how to plan searches
├── search_agent.py # Executes search tasks
├── writer_agent.py # Writes the final report
├── email_agent.py # Handles email sending
├── requirements.txt # Dependencies
└── README.md # This file



## 🚀 How to Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/DeepResearch
cd DeepResearch

# Install dependencies
uv pip install -r requirements.txt

# Run the app
uv run deep_research.py

🔐 Environment Variables (.env)

OPENAI_API_KEY=your_openai_key
SENDGRID_API_KEY=your_sendgrid_key
EMAIL_FROM=your_verified_sender@example.com
EMAIL_TO=recipient@example.com


🧩 Tech Stack
OpenAI Assistants (via openai-agents)

Gradio (v5.29.0)

Python 3.12+

asyncio

SendGrid for email delivery

📬 Feedback
Feel free to open an issue or leave a comment on the Hugging Face space if you have suggestions or encounter problems.


