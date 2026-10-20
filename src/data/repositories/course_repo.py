from mysql.connector import Error

from src.data.connection import get_connection


class CourseRepository:
    def create(self, instructor_id, title, description, duration):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO courses (instructor_id, title, description, duration) "
                "VALUES (%s, %s, %s, %s)"
            )
            cursor.execute(sql, (instructor_id, title, description, duration))
            conn.commit()
            return cursor.lastrowid
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, instructor_id, title, description, duration, created_at "
                "FROM courses WHERE id = %s"
            )
            cursor.execute(sql, (course_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def list_by_instructor(self, instructor_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, title, description, duration, created_at "
                "FROM courses WHERE instructor_id = %s ORDER BY id"
            )
            cursor.execute(sql, (instructor_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def list_all(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT c.id, c.title, c.description, c.duration, "
                "u.first_name AS instructor_first_name, u.last_name AS instructor_last_name "
                "FROM courses c JOIN users u ON c.instructor_id = u.id "
                "ORDER BY c.id"
            )
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def update(self, course_id, title, description, duration):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "UPDATE courses SET title = %s, description = %s, duration = %s "
                "WHERE id = %s"
            )
            cursor.execute(sql, (title, description, duration, course_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, course_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM courses WHERE id = %s"
            cursor.execute(sql, (course_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
