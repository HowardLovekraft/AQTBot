from os import getenv
from dotenv import load_dotenv

load_dotenv(dotenv_path="env\\venv.env")
def get_token():
    token = getenv('TOKEN_API')
    return token

def get_user():
    user = getenv('DB_USER')
    return user

def get_pass():
    password = getenv('DB_PASS')
    return password

def get_host():
    host = getenv('DB_HOST')
    return host

def get_port():
    port = getenv('DB_POR')
    return port

def get_name():
    name = getenv('DB_NAME')
    return name
