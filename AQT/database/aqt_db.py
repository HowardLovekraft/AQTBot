import psycopg2 as pg
from AQT.other.messages import INTERVIEWER_MODE, INTERVIEWEE_MODE
from AQT.env.env_reader import get_pass, get_user, get_host, get_name, get_port


# Подключиться к существующей базе данных/создать базу данных
async def db_connect():
    global db, cur
    db = pg.connect(user=get_user(),
                    password=get_pass(),
                    host=get_host(),
                    port=get_port(),
                    database=get_name())
    cur = db.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS questions (
    interviewer INTEGER,
    interviewee INTEGER,
    question INTEGER, 
    thread TEXT NOT NULL
    );'''
    cur.execute(create_table_query)
    db.commit()

# взять из thread все данные. Если thread_id там нет - в бд ввести:
# в interviewee - chat_id
# в thread - thread_id. Вернуть все вот это.
# иначе - вернуть False.
# короче вводит thread в БД
async def create_new_thread(chat_id, thread_id):
    cur.execute("SELECT thread FROM questions")
    all_ids = cur.fetchall()
    db.commit()
    if thread_id not in all_ids:
        aqthread = cur.execute("INSERT INTO questions (interviewee, thread) VALUES (%s, %s)", (chat_id, thread_id))
        db.commit()
        return aqthread
    else:
        return False

# взять из thread все данные. Если thread_id там нет - в бд ввести
# interviewer - chat_id
# question - question_id соотвественно
async def create_new_interviewer(chat_id, question_id, thread_id):
    cur.execute("SELECT thread FROM questions")
    all_ids = cur.fetchall()
    db.commit()
    if thread_id not in all_ids:
        aqthread = cur.execute("UPDATE questions SET (interviewer, question) = (%s, %s) WHERE thread = %s", (chat_id, question_id, thread_id,))
        db.commit()
        return aqthread
    else:
        return False

# выбрать thread где thread == code. Если все верно - вернуть True, иначе False.
# проверка на существование code в БД, короче
async def check_thread_id(code):
    cur.execute("SELECT thread FROM questions WHERE thread = %s", (code,))
    id = cur.fetchone()
    db.commit()
    if id:
        return True
    else:
        return False

# выбрать thread, где interviewee == user. Вернуть его
async def get_thread_id(user):
    cur.execute("SELECT thread FROM questions WHERE interviewee = %s", (user,))
    id = cur.fetchone()
    db.commit()
    return id

# если INTERVIEWEE - выбрать interviewee где thread == state и вернуть его
# если INTERVIEWER - выбрать interviewer где thread == state и вернуть его
# возвращает chat_id человека с нужной ролью, короче
async def get_user_id(role, state):
    if role == INTERVIEWEE_MODE:
        cur.execute('SELECT interviewee FROM questions WHERE thread = %s', (state,))
    elif role == INTERVIEWER_MODE:
        cur.execute('SELECT interviewer FROM questions WHERE thread = %s', (state,))
    member = cur.fetchone()
    db.commit()
    return member

# выбрать все из question. Если message_id в question - выбрать question где он == message_id.
# вернуть его.
# иначе - False
async def get_question_id(message_id):
    cur.execute("SELECT question FROM questions")
    all_ids = cur.fetchall()
    db.commit()
    if (message_id,) in all_ids:
        cur.execute("SELECT question FROM questions WHERE question = %s", (message_id,))
        question_id = cur.fetchone()
        db.commit()
        return question_id
    else:
        return False


# заготовка под
# cur.close()
# db.close()
# print("Соединение с PostgreSQL закрыто")
