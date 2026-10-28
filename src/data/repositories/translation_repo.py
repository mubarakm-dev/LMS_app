from mysql.connector import Error

from src.data.connection import get_connection

# question_translations: id, question_id, language, question_text, option_a..option_d,
#                        source_updated_at, created_at, UNIQUE (question_id, language)
#



class TranslationRepository:
    def get(self, question_id, language):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT question_id, language, question_text, option_a, option_b, "
                "option_c, option_d, source_updated_at "
                "FROM question_translations WHERE question_id = %s AND language = %s"
            )
            cursor.execute(sql, (question_id, language))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def save(self, question_id, language, question_text, option_a, option_b, option_c,
             option_d, source_updated_at):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = (
                "INSERT INTO question_translations "
                "(question_id, language, question_text, option_a, option_b, option_c, "
                " option_d, source_updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "question_text = VALUES(question_text), option_a = VALUES(option_a), "
                "option_b = VALUES(option_b), option_c = VALUES(option_c), "
                "option_d = VALUES(option_d), source_updated_at = VALUES(source_updated_at), "
                "created_at = CURRENT_TIMESTAMP"
            )
            cursor.execute(sql, (question_id, language, question_text, option_a, option_b,
                                 option_c, option_d, source_updated_at))
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def list_for_quiz(self, quiz_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = (
                "SELECT t.question_id, t.language, "
                "(t.source_updated_at = q.updated_at) AS is_fresh "
                "FROM question_translations t "
                "JOIN questions q ON t.question_id = q.id "
                "WHERE q.quiz_id = %s"
            )
            cursor.execute(sql, (quiz_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
