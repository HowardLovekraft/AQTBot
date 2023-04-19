import sqlite3 as sq


async def db_connect() -> None:
    global db, cur
    db = sq.connect('aqt.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS questions(interviewee TEXT, thread TEXT, interviewer TEXT)")
    db.commit()

async def create_new_thread(chat_id, thread_id):
    aqthread = cur.execute("INSERT INTO questions (interviewee, thread) VALUES (?, ?)", (chat_id, thread_id))
    db.commit()
    return aqthread

async def check_thread_id(code):
    id = cur.execute("SELECT thread FROM questions WHERE thread = ?", (code,)).fetchone()
    if id:
        return True
    else:
        return False


#async def set_interviewer(user):
#    interviewer = cur.execute('INSERT INTO questions (interviewer) VALUES (?)', (user))
#    db.commit()
#    return interviewer

async def get_interviewee_id(state):
    aqt_question = cur.execute('SELECT interviewee FROM questions WHERE thread = ?', (state,)).fetchone()
    db.commit()
    return aqt_question

