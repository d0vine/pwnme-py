#!/usr/bin/env python
from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from db_wrapper import get_db
from collections import namedtuple

app = Flask(__name__)

Article = namedtuple('Article', ['id', 'name', 'content', 'author'])
User = namedtuple('User', ['id', 'username', 'password', 'role'])


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/articles')
def article_list():
    cur = get_db().cursor()
    articles = cur.execute('select * from articles').fetchall()
    return render_template('articles.html', articles=[Article(*art) for art in articles])


@app.route('/articles/<article_id>')
def single_article(article_id):
    cur = get_db().cursor()
    article = cur.execute('select * from articles where id={}'.format(article_id)).fetchone()
    return render_template('single_article.html', article=Article(*article))


@app.route('/articles/<article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    cur = get_db().cursor()
    if request.method == 'GET':
        article = cur.execute('select * from articles where id={}'.format(article_id)).fetchone()
        return render_template('edit_article.html', article=Article(*article))
    else:
        data = request.form
        update_string = ", ".join(
            ["{}={}".format(
                key, value if type(value) == int else "'{}'".format(value.replace("'", "''"))
            ) for key, value in data.items()]
        )
        query = 'update articles set {} where id={}'.format(update_string, article_id)
        print(query)
        cur.execute(query)
        get_db().commit()
        return redirect('/articles/{}'.format(article_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # check login status
        return redirect('/articles')
    else:
        return render_template('login.html')


@app.route('/users')
def user_list():
    # TODO: check role
    # 401 if not admin
    # 403 if not logged in
    cur = get_db().cursor()
    users = cur.execute('select * from users').fetchall()
    return render_template('users.html', users=[User(*user) for user in users])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
