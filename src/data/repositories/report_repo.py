from src.data.connection import get_connection


class ReportRepository:
    def course_performance(self, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT u.id, u.first_name, u.last_name, u.email, "
                "(SELECT COUNT(DISTINCT r.quiz_id) FROM quiz_results r "
                " JOIN quizzes q ON r.quiz_id = q.id "
                " WHERE q.course_id = %s AND r.user_id = u.id) AS quizzes_attempted, "
                "(SELECT COUNT(*) FROM submissions s "
                " JOIN assignments a ON s.assignment_id = a.id "
                " WHERE a.course_id = %s AND s.user_id = u.id) AS assignments_submitted, "
                "(SELECT ROUND(AVG(s.score), 2) FROM submissions s "
                " JOIN assignments a ON s.assignment_id = a.id "
                " WHERE a.course_id = %s AND s.user_id = u.id AND s.score IS NOT NULL) "
                " AS avg_assignment_score "
                "FROM enrollments e "
                "JOIN users u ON e.user_id = u.id "
                "WHERE e.course_id = %s "
                "ORDER BY u.last_name, u.first_name"
            )
            cursor.execute(sql, (course_id, course_id, course_id, course_id))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def student_quiz_results(self, user_id, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT q.id AS quiz_id, q.title AS quiz_title, q.total_marks, "
                "COUNT(r.id) AS attempts, MAX(r.score) AS best_score, "
                "MAX(r.attempted_at) AS last_attempt "
                "FROM quiz_results r "
                "JOIN quizzes q ON r.quiz_id = q.id "
                "WHERE q.course_id = %s AND r.user_id = %s "
                "GROUP BY q.id, q.title, q.total_marks "
                "ORDER BY q.id"
            )
            cursor.execute(sql, (course_id, user_id))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def student_assignment_marks(self, user_id, course_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT a.id AS assignment_id, a.title AS assignment_title, a.max_marks, "
                "s.submitted_at, s.score, s.feedback, s.released "
                "FROM submissions s "
                "JOIN assignments a ON s.assignment_id = a.id "
                "WHERE a.course_id = %s AND s.user_id = %s "
                "ORDER BY a.id"
            )
            cursor.execute(sql, (course_id, user_id))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
