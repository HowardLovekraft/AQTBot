import sqlite3 as sq

async def db_connect() -> None:
    global db, cur
    db = sq.connect('aqt.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS questions(interviewee TEXT, interviewer NUMBER, question NUMBER, thread TEXT)")
    db.commit()

async def create_new_thread(chat_id, thread_id):
    all_ids = cur.execute("SELECT thread FROM questions").fetchall()
    db.commit()
    if thread_id not in all_ids:
        aqthread = cur.execute("INSERT INTO questions (interviewee, thread) VALUES (?, ?)", (chat_id, thread_id))
        db.commit()
        return aqthread
    else:
        return False

async def create_new_interviewer(chat_id, question_id, thread_id):
    all_ids = cur.execute("SELECT thread FROM questions").fetchall()
    db.commit()
    if thread_id not in all_ids:
        aqthread = cur.execute("UPDATE questions SET (interviewer, question) = (?, ?) WHERE thread = ?", (chat_id, question_id, thread_id,)).fetchall()
        db.commit()
        return aqthread
    else:
        return False

async def check_thread_id(code):
    id = cur.execute("SELECT thread FROM questions WHERE thread = ?", (code,)).fetchone()
    if id:
        return True
    else:
        return False

async def get_thread_id(user):
    id = cur.execute("SELECT thread FROM questions WHERE interviewee = ?", (user,)).fetchone()
    return id

async def get_user_id(role, state):
    if role == "interviewee":
        member = cur.execute('SELECT interviewee FROM questions WHERE thread = ?', (state,)).fetchone()
    if role == "interviewer":
        member = cur.execute('SELECT interviewer FROM questions WHERE thread = ?', (state,)).fetchone()
    db.commit()
    return member


async def get_question_id(message_id):
    all_ids = cur.execute("SELECT question FROM questions").fetchall()
    db.commit()
    if (message_id,) in all_ids:
        question_id = cur.execute("SELECT question FROM questions WHERE question = ?", (message_id,)).fetchone()
        db.commit()
        return question_id
    else:
        return False