import psycopg2
import os
import validators

from dotenv import load_dotenv
from flask import (
    flash,
    Flask,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for
)
from page_analyzer.url_repository import UrlRepository
from urllib.parse import urlparse, urlunparse

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlRepository(app.config['DATABASE_URL'])


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/urls/')
def urls_get():
    messages = get_flashed_messages(with_categories=True)
    urls = repo.get_content()
    return render_template(
        'urls/index.html',
        urls=urls,
        messages=messages
    )


@app.post('/urls')
def urls_post():
    url_data = request.form.to_dict()
    norm_url = normalize_url(url_data['name'])
    url_data['name'] = norm_url
    error = validate(norm_url)
    if error:
        return render_template(
            'index.html',
            error=error,
        ), 422
    repo.save(url_data)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('urls_get'), code=302)


def validate(url):
    error = ''
    if not url['name']:
        error = "Заполните поле"
    elif not validators.url(url['name']):
        error = "Некорректный URL"
    return error


def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_scheme = parsed_url.scheme.lower()
    normalized_netloc = parsed_url.netloc.lower()
    normalized_path = "/".join(segment.strip("/") for segment in parsed_url.path.split("/"))
    normalized_parsed_url = parsed_url._replace(scheme=normalized_scheme, netloc=normalized_netloc, path=normalized_path)
    normalized_url = urlunparse(normalized_parsed_url)
    return normalized_url