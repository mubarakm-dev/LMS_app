from mysql.connector import Error

from src.data.connection import get_connection


class VerificationRepo:
    def save_code(self, user_id, code, expires_at):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO email_verifications (user_id, code, expires_at) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user_id, code, expires_at))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_latest(self, user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM email_verifications WHERE user_id = %s ORDER BY id DESC LIMIT 1"
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def increment_attempts(self, verification_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE email_verifications SET attempts = attempts + 1 WHERE id = %s"
            cursor.execute(sql, (verification_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_for_user(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM email_verifications WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
