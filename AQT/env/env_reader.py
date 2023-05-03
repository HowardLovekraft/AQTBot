from os import getenv
from dotenv import load_dotenv
def get_token():
    load_dotenv(dotenv_path="env\\venv.env")
    token = getenv('TOKEN_API')
    return token

