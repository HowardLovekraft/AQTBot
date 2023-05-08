import psycopg2 as pg
from AQT.other.messages import INTERVIEWER_MODE, INTERVIEWEE_MODE
from AQT.env.env_reader import get_pass, get_user, get_host, get_name, get_port

# Подключиться к существующей базе данных
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

async def check_thread_id(code):
    cur.execute("SELECT thread FROM questions WHERE thread = %s", (code,))
    id = cur.fetchone()
    db.commit()
    if id:
        return True
    else:
        return False

async def get_thread_id(user):
    cur.execute("SELECT thread FROM questions WHERE interviewee = %s", (user,))
    id = cur.fetchone()
    db.commit()
    return id

async def get_user_id(role, state):
    if role == INTERVIEWEE_MODE:
        cur.execute('SELECT interviewee FROM questions WHERE thread = %s', (state,))
    elif role == INTERVIEWER_MODE:
        cur.execute('SELECT interviewer FROM questions WHERE thread = %s', (state,))
    member = cur.fetchone()
    db.commit()
    return member


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


# cur.close()
# db.close()
# print("Соединение с PostgreSQL закрыто")