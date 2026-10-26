from mysql.connector import Error, IntegrityError

from src.data.connection import get_connection
from src.domain.errors import DuplicateError

# submissions: id, assignment_id, user_id, submission_link, score (NULL until graded), feedback, released, submitted_at
# UNIQUE (assignment_id, user_id)


class SubmissionRepository:
    def create(self, assignment_id, user_id, submission_link):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO submissions (assignment_id, user_id, submission_link) "
                "VALUES (%s, %s, %s)"
            )
            cursor.execute(sql, (assignment_id, user_id, submission_link))
            conn.commit()
            return cursor.lastrowid
        except IntegrityError:
            conn.rollback()
            raise DuplicateError("You have already submitted this assignment.")
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_for_student(self, assignment_id, user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, assignment_id, submission_link, score, feedback, released, submitted_at "
                "FROM submissions WHERE assignment_id = %s AND user_id = %s"
            )
            cursor.execute(sql, (assignment_id, user_id))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def list_by_student(self, user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT s.id, a.title AS assignment_title, c.title AS course_title, "
                "a.max_marks, s.submission_link, s.submitted_at, "
                "s.score, s.feedback, s.released "
                "FROM submissions s "
                "JOIN assignments a ON s.assignment_id = a.id "
                "JOIN courses c ON a.course_id = c.id "
                "WHERE s.user_id = %s "
                "ORDER BY s.submitted_at DESC"
            )
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def list_for_assignment(self, assignment_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT s.id, u.first_name, u.last_name, u.email, "
                "s.submission_link, s.submitted_at, s.score, s.feedback, s.released "
                "FROM submissions s "
                "JOIN users u ON s.user_id = u.id "
                "WHERE s.assignment_id = %s "
                "ORDER BY s.submitted_at"
            )
            cursor.execute(sql, (assignment_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, submission_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, assignment_id, user_id, submission_link, score, feedback, released, submitted_at "
                "FROM submissions WHERE id = %s"
            )
            cursor.execute(sql, (submission_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def grade(self, submission_id, score, feedback):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE submissions SET score = %s, feedback = %s WHERE id = %s"
            cursor.execute(sql, (score, feedback, submission_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def release(self, submission_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE submissions SET released = TRUE WHERE id = %s AND score IS NOT NULL"
            cursor.execute(sql, (submission_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def release_all_graded(self, assignment_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "UPDATE submissions SET released = TRUE "
                "WHERE assignment_id = %s AND score IS NOT NULL"
            )
            cursor.execute(sql, (assignment_id,))
            conn.commit()
            return cursor.rowcount
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
