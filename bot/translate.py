import os
import logging
from google.cloud import translate
from google.oauth2 import service_account

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_PRIVATE_KEY_ID = os.getenv('GOOGLE_PRIVATE_KEY_ID')
GOOGLE_PRIVATE_KEY = os.getenv('GOOGLE_PRIVATE_KEY').replace(r'\n', '\n')
GOOGLE_CLIENT_EMAIL = os.getenv('GOOGLE_CLIENT_EMAIL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_509_CERT = os.getenv('GOOGLE_509_CERT')

credentials = service_account.Credentials.from_service_account_info(
    {
      "type": "service_account",
      "project_id": "encouraging-art-378908",
      "private_key_id": GOOGLE_PRIVATE_KEY_ID,
      "private_key": GOOGLE_PRIVATE_KEY,
      "client_email": GOOGLE_CLIENT_EMAIL,
      "client_id": GOOGLE_CLIENT_ID,
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": GOOGLE_509_CERT
    }
)

def translate_text(text: str, project_id="encouraging-art-378908"):
    logger.info('Google Translate: send request.')
    try:
        client = translate.TranslationServiceClient(credentials=credentials)
        location = "global"
        parent = f"projects/{project_id}/locations/{location}"

        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "source_language_code": "en-US",
                "target_language_code": "uk",
            }
        )

        logger.info('Google Translate: translation acquired.')
        return response.translations[0].translated_text
    except Exception as error:
        raise error