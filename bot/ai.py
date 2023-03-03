import os
import logging
import openai

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_response(messages: list) -> str:
    logger.info(f'OpenAI: Requesting reply')
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages
    )
    logger.info(f'OpenAI: Reply generated. Total tokens: {response.usage.total_tokens}')
    message = response.choices[0].message.content
    return message.strip() if message else 'No reply ;_;'
