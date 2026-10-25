from mysql.connector import Error, IntegrityError
from src.data.connection import get_connection
from src.domain.errors import DuplicateError

class LessonRepository:
    def create(self, course_id, title, content, video_url, lesson_order):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO lessons (course_id, title, content, video_url, lesson_order) VALUES (%s, %s, %s, %s, %s)"
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

    def next_order(course_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO lessons (course_id) VALUES (%s)"
            cursor.execute(sql, (course_id))
            
                    
        except IntegrityError:
            conn.rollback()
            raise DuplicateError("A lesson already has that position.")
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
        

