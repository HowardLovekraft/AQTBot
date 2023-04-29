import secrets
import string
import asyncio
import database.aqt_db


async def generate_random_code():
    letters = string.ascii_uppercase
    return ''.join(secrets.choice(letters) for i in range(6))

async def generator():
    return await generate_random_code()