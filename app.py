import logging
import os

import gradio as gr

from docchat.chat_engine import ChatEngine

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# Create a Gradio application with a title
with gr.Blocks(title="DocChat") as demo:
    # Define a function to create a chatbot and initialize it
    def make_chatbot(filesson):
        global chat_engine

        chat_engine = ChatEngine(filesson)  # Initialize the chat engine
        return {chat_column: gr.Column(visible=True)}

    # Define a function to set the OpenAI API key
    def set_api_key(api_key):
        """Set the OpenAI API key using the provided value.

        Args:
            api_key (str): The OpenAI API key.
        """
        os.environ["OPENAI_API_KEY"] = api_key

    api_key = gr.Textbox(label="OpenAI API Key", placeholder="sk-...")
    api_key.change(set_api_key, [api_key])

    # Create a file uploader
    files = gr.Files()
    run_btn = gr.Button()

    # Create a chatbot component
    with gr.Column(visible=False) as chat_column:
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="Message")
        clear = gr.Button("Clear")

        # Define a function to respond to user messages
        def respond(user_message, chat_history):
            """Respond to a user's message and update the chat history.

            Args:
                user_message (str): The user's message.
                chat_history (List[Tuple[str, str]]): List of user messages and responses.

            Returns:
                Tuple[str, List[Tuple[str, str]]]: A tuple with an empty string and the updated chat history.
            """
            response = chat_engine.run(user_message, [tuple(x) for x in chat_history])
            chat_history.append((user_message, response))
            return "", chat_history

        msg.submit(respond, [msg, chatbot], [msg, chatbot], queue=False)
        clear.click(lambda: None, None, chatbot, queue=False)

    # Add a callback for the run button to create the chatbot
    run_btn.click(make_chatbot, [files], [chat_column])

# Launch the Gradio application with the option to share it
demo.launch(share=False)
