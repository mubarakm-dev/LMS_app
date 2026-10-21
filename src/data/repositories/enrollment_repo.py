from mysql.connector import Error, IntegrityError

from src.data.connection import get_connection
from src.domain.errors import DuplicateError

# enrollments: id, user_id, course_id, enrolled_at, status ('active'|'completed'|'dropped'), UNIQUE (user_id, course_id)


class EnrollmentRepository:
    def create(self, user_id, course_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO enrollments (user_id, course_id) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, course_id))
            conn.commit()
            return cursor.lastrowid
        except IntegrityError:
            conn.rollback()
            raise DuplicateError("You are already enrolled in this course.")
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def exists(self, user_id, course_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT 1 FROM enrollments WHERE user_id = %s AND course_id = %s"
            cursor.execute(sql, (user_id, course_id))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    def list_by_student(self, user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT c.id, c.title, c.duration, e.status, e.enrolled_at, "
                "u.first_name AS instructor_first_name, u.last_name AS instructor_last_name "
                "FROM enrollments e "
                "JOIN courses c ON e.course_id = c.id "
                "JOIN users u ON c.instructor_id = u.id "
                "WHERE e.user_id = %s "
                "ORDER BY e.enrolled_at DESC"
            )
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def list_students_for_course(self, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT u.id, u.first_name, u.last_name, u.email, e.status, e.enrolled_at "
                "FROM enrollments e "
                "JOIN users u ON e.user_id = u.id "
                "WHERE e.course_id = %s "
                "ORDER BY u.last_name, u.first_name"
            )
            cursor.execute(sql, (course_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
