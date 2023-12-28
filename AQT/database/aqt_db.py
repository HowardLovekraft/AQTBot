import psycopg as pg
from AQT.other.messages import INTERVIEWER_MODE, INTERVIEWEE_MODE
from AQT.env.env_reader import get_pass, get_user, get_host, get_name, get_port


async def db_connect():
    # Подключиться к существующей базе данных/создать базу данных
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            create_table_query = """CREATE TABLE IF NOT EXISTS questions (
            interviewer INTEGER,
            interviewee INTEGER,
            question TEXT, 
            thread TEXT NOT NULL
            );"""
            cur.execute(create_table_query)
            conn.commit()


async def create_new_thread(chat_id, thread_id):
    """
    взять из thread все данные. Если thread_id там нет - в бд ввести:
    в interviewee - chat_id
    в thread - thread_id. Вернуть все вот это.
    иначе - вернуть False.
    короче вводит thread в БД
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread FROM questions")
            all_ids = cur.fetchall()
            conn.commit()
            if thread_id not in all_ids:
                aqthread = cur.execute("INSERT INTO questions (interviewee, thread) VALUES (%s, %s)",
                                       (chat_id, thread_id))
                conn.commit()
                return aqthread
            else:
                return False


async def create_new_interviewer(chat_id, question_id, thread_id):
    """
    взять из thread все данные. Если thread_id там нет - в бд ввести
    interviewer - chat_id
    question - question_id соотвественно
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                          port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread FROM questions")
            all_ids = cur.fetchall()
            conn.commit()
            if thread_id not in all_ids:
                aqthread = cur.execute("UPDATE questions SET (interviewer, question) = (%s, %s) WHERE thread = %s",
                                       (chat_id, question_id, thread_id,))
                conn.commit()
                return aqthread
            else:
                return False


async def check_thread_id(code):
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
    # выбрать thread, где interviewee == user. Вернуть его
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread FROM questions WHERE interviewee = %s",
                        (user,))
            id = cur.fetchone()
            conn.commit()
            return id


async def get_user_id(role, state):
    """
    если INTERVIEWEE - выбрать interviewee где thread == state и вернуть его
    если INTERVIEWER - выбрать interviewer где thread == state и вернуть его
    возвращает chat_id человека с нужной ролью, короче
    """
    with pg.connect(user=get_user(), password=get_pass(), host=get_host(),
                    port=get_port(), dbname=get_name()) as conn:
        with conn.cursor() as cur:
            if role == INTERVIEWEE_MODE:
                cur.execute('SELECT interviewee FROM questions WHERE thread = %s',
                            (state,))
            elif role == INTERVIEWER_MODE:
                cur.execute('SELECT interviewer FROM questions WHERE thread = %s',
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
