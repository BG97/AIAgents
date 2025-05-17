import gradio as gr
from search import Search


async def setup():
    search = Search()
    await search.setup()
    return search

async def process_message(search, username, message, success_criteria, history):
    results = await search.run_superstep(message, username, success_criteria, history)
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


with gr.Blocks(title="Search", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## Search Personal Co-Worker")
    search = gr.State(delete_callback=free_resources)
    
    with gr.Row():
        chatbot = gr.Chatbot(label="Search", height=300, type="messages")
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