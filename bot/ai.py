import os
import logging
import openai
from datetime import datetime

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

# taras 0.1: 'Your name is Taras. You are sad and cynic, make cringe jokes on user messages.'

current_date = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")
based_messages = [
    {'role': 'system', 'content': 'Your name is Taras. You are ukrainian.'
                                  'You are sad and cynic but do not take it seriously, make cringe jokes on user messages. '
                                  f'Current date: {current_date}'},
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
