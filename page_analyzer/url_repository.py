from datetime import date

import psycopg2
from psycopg2.extras import RealDictCursor


class UrlRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def get_content(self):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls " 
                "LEFT JOIN (SELECT url_id, MAX(created_at) AS latest_check " 
                "FROM url_checks GROUP BY url_id) checks " 
                "ON urls.id = checks.url_id " 
                "ORDER BY urls.id DESC")
                return cur.fetchall()

    def find(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                return cur.fetchone()

    def get_by_term(self, search_term=""):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", 
                (search_term,))
                return cur.fetchone()

    def save(self, url_data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO urls (name, created_at) "
                    "VALUES (%s, %s) RETURNING id",
                    (url_data['name'], date.today())
                )
                url_data['id'] = cur.fetchone()[0]
            conn.commit()
        return url_data['id']

    def destroy(self, id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls WHERE id = %s", (id,))
            conn.commit()