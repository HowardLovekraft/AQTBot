import string
import database.aqt_db as aqt_db


async def checker(message_text: str) -> bool:
    if (len(message_text) == 6 and
            message_text.count(string.whitespace) == 0 and
            message_text.count(string.punctuation) == 0 and
            await aqt_db.check_thread_id(message_text)):
        return True
    return False


async def code_checker(message_text: str) -> bool:
    return await checker(message_text)
