import uuid
from datetime import datetime

import psycopg2
from decouple import config

DATABASE_URL = config('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """
    Create the prompts table if it doesn't exist yet. Safe to call on every app startup.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    prompt_id UUID PRIMARY KEY,
                    user_token TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT,
                    timestamp TIMESTAMPTZ NOT NULL
                )
            """)
        conn.commit()


def create_user():
    """
    Create an anonymous user identifier for the session.

    Returns:
        str: A newly generated user token.
    """
    return str(uuid.uuid4())


def post_prompt(prompt, user_token):
    """
    Insert a prompt into the database with a unique identifier and 'None' status initially.

    Args:
        prompt (str): The prompt to post.
        user_token (str): The user's token.

    Returns:
        str or None: The unique prompt identifier if posted successfully, None otherwise.
    """
    prompt_id = str(uuid.uuid4())
    timestamp = datetime.now()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO prompts (prompt_id, user_token, prompt, status, timestamp) VALUES (%s, %s, %s, %s, %s)",
                    (prompt_id, user_token, prompt, None, timestamp)
                )
            conn.commit()
        print("Prompt inserted successfully with 'None' status, prompt_id:", prompt_id)
        return prompt_id
    except Exception as e:
        print("Error inserting prompt:", e)
        return None


def update_prompt_status(prompt_id, is_success, user_token):
    """
    Update the status of a specific prompt in the database using its unique identifier.

    Args:
        prompt_id (str): The unique identifier of the prompt to update.
        is_success (bool): Whether the prompt was answered successfully.
        user_token (str): The user's token, scoping the update to their own prompt.
    """
    if prompt_id is None:
        print("Error updating prompt status: prompt_id is None")
        return

    status = "successful" if is_success else "unsuccessful"

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE prompts SET status = %s, timestamp = %s WHERE prompt_id = %s AND user_token = %s",
                    (status, datetime.now(), prompt_id, user_token)
                )
            conn.commit()
        print(f"Prompt '{prompt_id}' status updated to '{status}' successfully.")
    except Exception as e:
        print("Error updating prompt status:", e)
