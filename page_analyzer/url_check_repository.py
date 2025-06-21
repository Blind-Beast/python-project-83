from datetime import date

import psycopg2
from psycopg2.extras import RealDictCursor


class UrlCheckRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def get_content(self, url_id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM url_checks WHERE url_id = %s " 
                "ORDER BY id DESC", (url_id,))
                return cur.fetchall()

    def find(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM url_checks WHERE id = %s", (id,))
                return cur.fetchone()

    def get_by_term(self, search_term=""):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM url_checks WHERE name = %s", 
                (search_term,))
                return cur.fetchone()

    def save(self, url_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO url_checks (url_id, created_at) "
                    "VALUES (%s, %s) RETURNING id",
                    (url_id, date.today())
                )
                url_check_id = cur.fetchone()[0]
            conn.commit()
        return url_check_id

    def destroy(self, id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM url_checks WHERE id = %s", (id,))
            conn.commit()