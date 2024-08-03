from os import getenv
from dotenv import load_dotenv
from typing import NamedTuple


class Vars(NamedTuple):
    user: str
    password: str
    host: str
    port: str
    dbname: str

class EnvVars:
    loader = load_dotenv(dotenv_path='env\\venv.env')
    if not loader:
        raise Exception("Couldn't load .env file. Var 'loader' is {loader}".format(loader=loader))

    token = getenv('TOKEN_API')
    vars = Vars(user=getenv('DB_USER'),
                password=getenv('DB_PASS'),
                host=getenv('DB_HOST'),
                port=getenv('DB_PORT'),
                dbname=getenv('DB_NAME'))
