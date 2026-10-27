from src.data.connection import get_connection


class StatsRepository:
    def get_overview(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT "
                "(SELECT COUNT(*) FROM users) AS total_users, "
                "(SELECT COUNT(*) FROM users WHERE role = 'student') AS students, "
                "(SELECT COUNT(*) FROM users WHERE role = 'instructor') AS instructors, "
                "(SELECT COUNT(*) FROM users WHERE role = 'admin') AS admins, "
                "(SELECT COUNT(*) FROM courses) AS courses, "
                "(SELECT COUNT(*) FROM enrollments) AS enrollments, "
                "(SELECT COUNT(*) FROM lessons) AS lessons, "
                "(SELECT COUNT(*) FROM assignments) AS assignments, "
                "(SELECT COUNT(*) FROM submissions) AS submissions, "
                "(SELECT COUNT(*) FROM quizzes) AS quizzes, "
                "(SELECT COUNT(*) FROM questions) AS questions, "
                "(SELECT COUNT(*) FROM quiz_results) AS quiz_attempts"
            )
            cursor.execute(sql)
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def top_courses(self, limit):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT c.id, c.title, u.first_name, u.last_name, COUNT(e.id) AS enrollments "
                "FROM courses c "
                "JOIN users u ON c.instructor_id = u.id "
                "LEFT JOIN enrollments e ON e.course_id = c.id "
                "GROUP BY c.id, c.title, u.first_name, u.last_name "
                "ORDER BY enrollments DESC, c.title "
                "LIMIT %s"
            )
            cursor.execute(sql, (limit,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
