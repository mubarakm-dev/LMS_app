from mysql.connector import Error, IntegrityError

from src.data.connection import get_connection
from src.domain.errors import DuplicateError

# lessons: id, course_id, title, content, video_url, lesson_order, created_at, UNIQUE (course_id, lesson_order)


class LessonRepository:
    def create(self, course_id, title, content, video_url, lesson_order):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO lessons (course_id, title, content, video_url, lesson_order) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cursor.execute(sql, (course_id, title, content, video_url, lesson_order))
            conn.commit()
            return cursor.lastrowid
        except IntegrityError:
            conn.rollback()
            raise DuplicateError("A lesson already has that position.")
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def next_order(self, course_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT COALESCE(MAX(lesson_order), 0) + 1 FROM lessons WHERE course_id = %s"
            cursor.execute(sql, (course_id,))
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()

    def list_by_course(self, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, title, content, video_url, lesson_order "
                "FROM lessons WHERE course_id = %s ORDER BY lesson_order"
            )
            cursor.execute(sql, (course_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, lesson_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, course_id, title, content, video_url, lesson_order, created_at "
                "FROM lessons WHERE id = %s"
            )
            cursor.execute(sql, (lesson_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def update(self, lesson_id, title, content, video_url):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE lessons SET title = %s, content = %s, video_url = %s WHERE id = %s"
            cursor.execute(sql, (title, content, video_url, lesson_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, lesson_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM lessons WHERE id = %s"
            cursor.execute(sql, (lesson_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
