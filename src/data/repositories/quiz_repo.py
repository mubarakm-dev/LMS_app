from mysql.connector import Error

from src.data.connection import get_connection

# quizzes: id, course_id, title, total_marks, duration (minutes), is_published, results_released, created_at


class QuizRepository:
    def create(self, course_id, title, duration):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO quizzes (course_id, title, duration) VALUES (%s, %s, %s)"
            cursor.execute(sql, (course_id, title, duration))
            conn.commit()
            return cursor.lastrowid
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, course_id, title, total_marks, duration, is_published, "
                "results_released, created_at "
                "FROM quizzes WHERE id = %s"
            )
            cursor.execute(sql, (quiz_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def list_by_course(self, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, title, total_marks, duration, is_published, results_released "
                "FROM quizzes WHERE course_id = %s ORDER BY id"
            )
            cursor.execute(sql, (course_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def list_published_by_course(self, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, title, total_marks, duration, results_released "
                "FROM quizzes WHERE course_id = %s AND is_published = TRUE ORDER BY id"
            )
            cursor.execute(sql, (course_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def update(self, quiz_id, title, duration):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE quizzes SET title = %s, duration = %s WHERE id = %s"
            cursor.execute(sql, (title, duration, quiz_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM quizzes WHERE id = %s"
            cursor.execute(sql, (quiz_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def set_published(self, quiz_id, published):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE quizzes SET is_published = %s WHERE id = %s"
            cursor.execute(sql, (published, quiz_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def set_results_released(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE quizzes SET results_released = TRUE WHERE id = %s"
            cursor.execute(sql, (quiz_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def refresh_total_marks(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "UPDATE quizzes SET total_marks = "
                "(SELECT COALESCE(SUM(marks), 0) FROM questions WHERE quiz_id = %s) "
                "WHERE id = %s"
            )
            cursor.execute(sql, (quiz_id, quiz_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
