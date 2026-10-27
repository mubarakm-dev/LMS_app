from mysql.connector import Error

from src.data.connection import get_connection

# quiz_results: id, quiz_id, user_id, score, language, attempted_at



class ResultRepository:
    def create(self, quiz_id, user_id, score, language):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO quiz_results (quiz_id, user_id, score, language) "
                "VALUES (%s, %s, %s, %s)"
            )
            cursor.execute(sql, (quiz_id, user_id, score, language))
            conn.commit()
            return cursor.lastrowid
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def list_by_student_and_quiz(self, user_id, quiz_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, score, language, attempted_at "
                "FROM quiz_results WHERE user_id = %s AND quiz_id = %s "
                "ORDER BY attempted_at, id"
            )
            cursor.execute(sql, (user_id, quiz_id))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def attempt_count(self, user_id, quiz_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT COUNT(*) FROM quiz_results WHERE user_id = %s AND quiz_id = %s"
            cursor.execute(sql, (user_id, quiz_id))
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()

    def best_score(self, user_id, quiz_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT MAX(score) FROM quiz_results WHERE user_id = %s AND quiz_id = %s"
            cursor.execute(sql, (user_id, quiz_id))
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()

    def summary_by_student(self, user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT q.id AS quiz_id, q.title AS quiz_title, c.title AS course_title, "
                "q.total_marks, q.results_released, "
                "COUNT(r.id) AS attempts, MAX(r.score) AS best_score "
                "FROM quiz_results r "
                "JOIN quizzes q ON r.quiz_id = q.id "
                "JOIN courses c ON q.course_id = c.id "
                "WHERE r.user_id = %s "
                "GROUP BY q.id, q.title, c.title, q.total_marks, q.results_released "
                "ORDER BY q.id"
            )
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def summary_for_quiz(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT u.id AS user_id, u.first_name, u.last_name, u.email, "
                "COUNT(r.id) AS attempts, MAX(r.score) AS best_score, "
                "ROUND(AVG(r.score), 2) AS average_score, MAX(r.attempted_at) AS last_attempt "
                "FROM quiz_results r "
                "JOIN users u ON r.user_id = u.id "
                "WHERE r.quiz_id = %s "
                "GROUP BY u.id, u.first_name, u.last_name, u.email "
                "ORDER BY u.last_name, u.first_name"
            )
            cursor.execute(sql, (quiz_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
