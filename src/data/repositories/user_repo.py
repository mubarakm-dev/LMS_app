from mysql.connector import Error, IntegrityError
from src.data.connection import get_connection

from src.domain.errors import DuplicateError




class UserRepository:
    def get_by_email(self, email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()


    def create(self, first_name, last_name, email, password_hash):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (first_name, last_name, email, password_hash))
            conn.commit()
            return cursor.lastrowid
        except IntegrityError:
            conn.rollback()
            raise DuplicateError("An account with that email already exists.")
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def email_exists(self, email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            sql = "SELECT 1 FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def mark_verified(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE users SET is_verified = TRUE WHERE id = %s"
            cursor.execute(sql, (user_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()


    def list_all(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, first_name, last_name, email, role, is_verified, is_active "
                "FROM users ORDER BY id"
            )
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, first_name, last_name, email, role, is_verified, is_active "
                "FROM users WHERE id = %s"
            )
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def update_role(self, user_id, role):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE users SET role = %s WHERE id = %s"
            cursor.execute(sql, (role, user_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

