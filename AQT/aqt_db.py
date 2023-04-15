import sqlite3 as sq


async def db_connect() -> None:
    global db, cur
    db = sq.connect('aqt.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS questions(user TEXT, thread TEXT, asker TEXT)")
    db.commit()

async def create_new_thread(chat_id, thread_id):
    aqthread = cur.execute("INSERT INTO questions (user, thread) VALUES (?, ?)", (chat_id, thread_id))
    db.commit()
    return aqthread


async def set_asker(user):
    orator = cur.execute('INSERT INTO questions (asker) VALUES (?)', (user,))
    db.commit()
    return orator

async def send_question(state):
    aqt_question = cur.execute('SELECT user FROM questions WHERE thread = ?', (state,)).fetchone()
    db.commit()
    return aqt_question

