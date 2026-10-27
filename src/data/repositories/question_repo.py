from mysql.connector import Error

from src.data.connection import get_connection

# questions: id, quiz_id, question_text, option_a..option_d, correct_option ('A'-'D'), marks, updated_at



class QuestionRepository:
    def create(self, quiz_id, question_text, option_a, option_b, option_c, option_d,
               correct_option, marks):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO questions "
                "(quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(sql, (quiz_id, question_text, option_a, option_b, option_c,
                                 option_d, correct_option, marks))
            conn.commit()
            return cursor.lastrowid
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, question_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, quiz_id, question_text, option_a, option_b, option_c, option_d, "
                "correct_option, marks, updated_at "
                "FROM questions WHERE id = %s"
            )
            cursor.execute(sql, (question_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def list_for_teacher(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, quiz_id, question_text, option_a, option_b, option_c, option_d, "
                "correct_option, marks, updated_at "
                "FROM questions WHERE quiz_id = %s ORDER BY id"
            )
            cursor.execute(sql, (quiz_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def list_for_student(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT id, question_text, option_a, option_b, option_c, option_d, marks "
                "FROM questions WHERE quiz_id = %s ORDER BY id"
            )
            cursor.execute(sql, (quiz_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_answer_key(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT id, correct_option, marks FROM questions WHERE quiz_id = %s"
            cursor.execute(sql, (quiz_id,))
            return {
                row["id"]: {"correct_option": row["correct_option"], "marks": row["marks"]}
                for row in cursor.fetchall()
            }
        finally:
            cursor.close()
            conn.close()

    def update(self, question_id, question_text, option_a, option_b, option_c, option_d,
               correct_option, marks):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "UPDATE questions SET question_text = %s, option_a = %s, option_b = %s, "
                "option_c = %s, option_d = %s, correct_option = %s, marks = %s "
                "WHERE id = %s"
            )
            cursor.execute(sql, (question_text, option_a, option_b, option_c, option_d,
                                 correct_option, marks, question_id))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete(self, question_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM questions WHERE id = %s"
            cursor.execute(sql, (question_id,))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
