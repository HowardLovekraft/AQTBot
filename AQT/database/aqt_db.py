import psycopg as pg
from env.env_reader import get_pass, get_user, get_host, get_name, get_port
from main import text_msgs
from aiogram.types import Message

async def db_connect():
    # Подключиться к существующей базе данных/создать базу данных
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            create_table_query = """CREATE TABLE IF NOT EXISTS questions (
            thread_owner BIGINT,
            thread_asker BIGINT,
            question BIGINT, 
            thread TEXT NOT NULL
            );"""
            cur.execute(create_table_query)
            conn.commit()


async def create_new_thread(chat_id: int, thread_id: str):
    """
    взять из колонки thread все данные. Если thread_id там нет - в бд ввести:
    в thread_owner - chat_id создателя ветки, передается на вход функции
    в thread - thread_id, создается функцией generator, код уже передается на вход.
    Вернуть все вот это.
    иначе - вернуть False.
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread FROM questions")
            all_ids = cur.fetchall()
            conn.commit()
            if thread_id not in all_ids:
                aqthread = cur.execute("INSERT INTO questions (thread_owner, thread) VALUES (%s, %s)",
                                       (chat_id, thread_id))
                conn.commit()
                return aqthread
            else:
                return False


async def create_new_asker(chat_id, question_id, thread_id):
    """
    взять из колонки thread все данные. Если thread_id там нет - в бд ввести
    thread_asker - chat_id
    question - question_id соотвественно
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread FROM questions")
            all_ids = cur.fetchall()
            conn.commit()
            if thread_id not in all_ids:
                aqthread = cur.execute("UPDATE questions SET (thread_asker, question) = (%s, %s) WHERE thread = %s",
                                       (chat_id, question_id, thread_id,))
                conn.commit()
                return aqthread
            else:
                return False


async def check_thread_id(code: str) -> bool:
    """
    выбрать thread где thread == code. Если все верно - вернуть True, иначе False.
    проверка на существование code в БД, короче
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread FROM questions WHERE thread = %s",
                        (code,))
            id = cur.fetchone()
            conn.commit()
            if id:
                return True
            else:
                return False


async def get_thread_id(user):
    # выбрать thread, где thread_owner == user. Вернуть его
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread FROM questions WHERE thread_owner = %s",
                        (user,))
            id = cur.fetchone()
            conn.commit()
            return id


async def get_user_id(role, state):
    """
    если THREADOWNER - выбрать thread_owner где thread == state и вернуть его
    если THREADASKER - выбрать thread_asker где thread == state и вернуть его
    возвращает chat_id человека с нужной ролью, короче
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            if role == text_msgs["THREADOWNER_MODE"]:
                cur.execute('SELECT thread_owner FROM questions WHERE thread = %s',
                            (state,))
            elif role == text_msgs["THREADASKER_MODE"]:
                cur.execute('SELECT thread_asker FROM questions WHERE thread = %s',
                            (state,))
            member = cur.fetchone()
            conn.commit()
            return member


async def get_question_id(message_id):
    """
    выбрать все из question. Если message_id в question - выбрать question где он == message_id.
    вернуть его.
    иначе - False
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT question FROM questions")
            all_ids = cur.fetchall()
            conn.commit()
            if (message_id,) in all_ids:
                cur.execute("SELECT question FROM questions WHERE question = %s",
                            (message_id,))
                question_id = cur.fetchone()
                conn.commit()
                return question_id
            else:
                return False
