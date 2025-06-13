from datetime import datetime

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
                cur.execute("SELECT * FROM urls")
                return cur.fetchall()

    def find(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                return cur.fetchone()

    def save(self, url_data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                if 'id' not in url_data:
                    # New url
                    cur.execute(
                        "INSERT INTO urls (name, created_at) "
                        "VALUES (%s, %s) RETURNING id",
                        (url_data['name'], datetime.now())
                    )
                    url_data['id'] = cur.fetchone()[0]
                else:
                    # Existing url
                    cur.execute(
                        "UPDATE urls SET name = %s, "
                        "created_at = %s WHERE id = %s",
                        (url_data['name'], datetime.now(), url_data['id'])
                    )
            conn.commit()
        return url_data['id']

    def destroy(self, id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls WHERE id = %s", (id,))
            conn.commit()