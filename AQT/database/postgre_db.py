import psycopg as pg
from pathlib import Path
from psycopg import sql
from datetime import date
from main import env_vars
from other.messages import ASKER_MODE, OWNER_MODE

constants = {
    "create_thread_owners_query": sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS thread_owners (
        owner_id INTEGER, 
        thread_code TEXT);
        """
    ),
    "create_thread_askers_query": sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS thread_askers (
        asker_id INTEGER,
        thread_code TEXT,
        message_id INTEGER);
        """
    ),
    "select_thread_code_column": sql.SQL(
        "SELECT thread_code FROM thread_owners"
    ),
    "insert_new_thread_owner": sql.SQL(
        "INSERT INTO thread_owners (owner_id, thread_code) VALUES (%s, %s)"
    ),
    "insert_new_thread_asker": sql.SQL(
        "INSERT INTO thread_askers (asker_id, thread_code, message_id) VALUES (%s, %s, %s)"
    ),
    "check_exact_thread_code": sql.SQL(
        "SELECT thread_code FROM thread_owners WHERE thread_code = %s"
    ),
    "get_exact_thread_code": sql.SQL(
        "SELECT thread_code FROM thread_askers WHERE asker_id = %s"
    ),
    "get_askers_questions_id": sql.SQL(
        "SELECT message_id FROM thread_askers"
    ),
    "get_exact_question_id": sql.SQL(
        "SELECT message_id FROM thread_askers WHERE message_id = %s"
    ),
    "get_owner_id_using_code": sql.SQL(
        'SELECT owner_id FROM thread_owners WHERE thread_code = %s'
    ),
    "get_asker_id_using_code": sql.SQL(
        'SELECT asker_id FROM thread_askers WHERE thread_code = %s'
    ),

    "backup_db_query": sql.SQL(
        "COPY %s TO {path} WITH (DELIMITER ';', HEADER TRUE);"
    ).format(path=str(Path.cwd()) + f"\\database\\backups\\aqt_bot_{date.today()}.sql"),
}


async def db_connect():
    # Подключиться к существующей базе данных/создать базу данных
    with pg.connect(**env_vars.vars._asdict()) as conn:
        with conn.cursor() as cur:
            cur.execute(constants["create_thread_owners_query"])
            cur.execute(constants["create_thread_askers_query"])
            conn.commit()


async def create_new_thread(owner_chat_id, thread_code):
    with pg.connect(**env_vars.vars._asdict()) as conn:
        with conn.cursor() as cur:
            all_codes = cur.execute(constants["select_thread_code_column"]).fetchall()
            conn.commit()
            if thread_code not in all_codes:
                aqthread = cur.execute(constants["insert_new_thread_owner"], (owner_chat_id, thread_code,))
                conn.commit()
                return aqthread
            else:
                return False


async def create_new_asker(question_msg_id, asker_chat_id, thread_code):
    with pg.connect(**env_vars.vars._asdict()) as conn:
        with conn.cursor() as cur:
            all_ids = cur.execute(constants["select_thread_code_column"]).fetchall()
            conn.commit()
            if thread_code not in all_ids:
                aqthread = cur.execute(constants["insert_new_thread_asker"],
                                       (asker_chat_id, thread_code, question_msg_id,))
                conn.commit()
                return aqthread
            else:
                return False


async def check_thread_id(code):
    with pg.connect(**env_vars.vars._asdict()) as conn:
        with conn.cursor() as cur:
            id = cur.execute(constants["check_exact_thread_code"], (code,)).fetchone()
            return True if id else False


async def get_thread_id(user):
    with pg.connect(**env_vars.vars._asdict()) as conn:
        with conn.cursor() as cur:
            id = cur.execute(constants["get_exact_thread_code"], (user,)).fetchone()
            return id


async def get_user_id(role, state):
    with pg.connect(**env_vars.vars._asdict()) as conn:
        with conn.cursor() as cur:
            if role == OWNER_MODE:
                member = cur.execute(constants["get_owner_id_using_code"], (state,)).fetchone()
            elif role == ASKER_MODE:
                member = cur.execute(constants["get_asker_id_using_code"], (state,)).fetchone()
            conn.commit()
            return member


async def get_question_id(message_id):
    with pg.connect(**env_vars.vars._asdict()) as conn:
        with conn.cursor() as cur:
            all_ids = cur.execute(constants["get_askers_questions_id"]).fetchall()
            conn.commit()
            if (message_id,) in all_ids:
                question_id = cur.execute(constants["get_exact_question_id"],
                                          (message_id,)).fetchone()
                conn.commit()
                return question_id
            else:
                return False
