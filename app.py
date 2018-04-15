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
def articles():
    cur = get_db().cursor()
    articles = cur.execute('select * from articles').fetchall()
    return render_template('articles.html', articles=[Article(*art) for art in articles])

@app.route('/articles/<article_id>')
def article(article_id):
    cur = get_db().cursor()
    article = cur.execute('select * from articles where id={}'.format(article_id)).fetchone()
    return render_template('single_article.html', article=Article(*article))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/articles')
    else:
        return render_template('login.html')

@app.route('/users')
def users():
    # TODO: check role
    cur = get_db().cursor()
    users = cur.execute('select * from users').fetchall()
    print(users)
    return render_template('users.html', users=[User(*user) for user in users])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
