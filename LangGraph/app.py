import gradio as gr
from search import Search
from langchain_core.messages import AIMessage

async def setup():
    search = Search()
    await search.setup()
    return search

async def process_message(search, username, message, success_criteria, history):
    results = await search.run_superstep(message, username, success_criteria, history)
    
    filter_messages(results)
    print(results)
    return results, search

async def reset():
    new_search = Search()
    await new_search.setup()
    return "", "","", None, new_search

def free_resources(search):
    print("Cleaning up")
    try:
        if search:
            search.free_resources()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


def filter_messages(results):
    if not results:
        return results
    
    ai_indices = [i for i, msg in enumerate(results) if msg.get('role') == 'assistant']
    
    if ai_indices:
        last_ai_index = ai_indices[-1]
        last_ai_message = results[last_ai_index]
        if "Evaluator Feedback" in last_ai_message.get('content', ''):
            results.pop(last_ai_index)
    
    return results

with gr.Blocks(title="Search", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## SearchOps_Assistant")
    search = gr.State(delete_callback=free_resources)

    with gr.Row():
        chatbot = gr.Chatbot(label="Search", height=500, type="messages")
    with gr.Group():
        with gr.Row():
            username = gr.Textbox(show_label=False, placeholder="Enter your username")
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to the Search")
        with gr.Row():
            success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")
        
    ui.load(setup, [], [search])
    message.submit(process_message, [search,username, message, success_criteria, chatbot], [chatbot, search])
    success_criteria.submit(process_message, [search, username, message, success_criteria, chatbot], [chatbot, search])
    go_button.click(process_message, [search, username, message, success_criteria, chatbot], [chatbot, search])
    reset_button.click(reset, [], [username, message, success_criteria, chatbot, search])

    
ui.launch(inbrowser=True)