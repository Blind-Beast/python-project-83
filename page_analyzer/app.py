import os
from urllib.parse import urlparse, urlunparse

import requests
import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.url_check_repository import UrlCheckRepository
from page_analyzer.url_repository import UrlRepository

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlRepository(app.config['DATABASE_URL'])
repo_checks = UrlCheckRepository(app.config['DATABASE_URL'])


@app.route("/")
def index():
    error = ''
    return render_template('index.html', error=error)


@app.route('/urls')
def urls_get():
    urls = repo.get_content()
    return render_template(
        'urls/index.html',
        urls=urls
    )


@app.post('/urls')
def urls_post():
    url_data = request.form.to_dict()
    norm_url = normalize_url(url_data['name'])
    error = validate(norm_url)
    if error:
        return render_template(
            'index.html',
            error=error,
        ), 422
    url_data['name'] = norm_url
    row = repo.get_by_term(url_data['name'])
    if row:
        flash('Страница уже существует', 'warning')
        return redirect(url_for("urls_show", id=row['id']))
    new_id = repo.save(url_data)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for("urls_show", id=new_id), code=302)


@app.post('/urls/<id>/checks')
def urls_checks_post(id):
    url = repo.find(id)
    response = requests.get(url['name'])
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'warning')
        return redirect(url_for("urls_show", id=id))
    repo_checks.save(id, response)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for("urls_show", id=id), code=302)


@app.route('/urls/<id>')
def urls_show(id):
    messages = get_flashed_messages(with_categories=True)
    url = repo.find(id)
    url_checks = repo_checks.get_content(id)
    return render_template(
        'urls/show.html',
        url=url,
        url_checks=url_checks,
        messages=messages
    )


def validate(url):
    error = ''
    if len(url) > 255:
        error = "URL превышает 255 символлов"
    elif not validators.url(url):
        error = "Некорректный URL"
    return error


def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_scheme = parsed_url.scheme.lower()
    normalized_netloc = parsed_url.netloc.lower()
    normalized_parsed_url = parsed_url._replace(
        scheme=normalized_scheme,
        netloc=normalized_netloc,
        path='/',
        query="",
        fragment=""
    )
    normalized_url = urlunparse(normalized_parsed_url)
    return normalized_url