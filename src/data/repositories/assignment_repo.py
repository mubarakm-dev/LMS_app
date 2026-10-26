from mysql.connector import Error

from src.data.connection import get_connection

# assignments: id, course_id, title, description, due_date (DATE), max_marks, created_at


class AssignmentRepository:
    def create(self, course_id, title, description, due_date, max_marks):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO assignments (course_id, title, description, due_date, max_marks) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cursor.execute(sql, (course_id, title, description, due_date, max_marks))
            conn.commit()
            return cursor.lastrowid
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, assignment_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, course_id, title, description, due_date, max_marks "
                "FROM assignments WHERE id = %s"
            )
            cursor.execute(sql, (assignment_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def list_by_course(self, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, course_id, title, description, due_date, max_marks "
                "FROM assignments WHERE course_id = %s ORDER BY due_date, id"
            )
            cursor.execute(sql, (course_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def update(self, assignment_id, title, description, due_date, max_marks):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "UPDATE assignments SET title = %s, description = %s, due_date = %s, max_marks = %s "
                "WHERE id = %s"
            )
            cursor.execute(sql, (title, description, due_date, max_marks, assignment_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, assignment_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM assignments WHERE id = %s"
            cursor.execute(sql, (assignment_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
