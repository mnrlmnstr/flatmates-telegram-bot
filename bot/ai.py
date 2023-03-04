import os
import logging
import openai

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

# taras 0.1: 'Your name is Taras. You are sad and cynic, make cringe jokes on user messages.'

based_messages = [
    {'role': 'system', 'content': 'Your name is Taras. You are sad and cynic, make cringe jokes on user messages.'},
]

def generate_response(messages: list) -> str:
    logger.info(f'OpenAI: Requesting reply')

    messages = based_messages + messages
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages
    )

    logger.info(f'OpenAI: Reply generated. Total tokens: {response.usage.total_tokens}')

    message = response.choices[0].message.content
    return message.strip()
