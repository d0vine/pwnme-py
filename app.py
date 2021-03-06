#!/usr/bin/env python
from binascii import hexlify
from binascii import unhexlify
from hashlib import md5
import pickle

from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from db_wrapper import get_db
from collections import namedtuple

app = Flask(__name__, static_url_path='/static')

Article = namedtuple('Article', ['id', 'name', 'content', 'author'])
User = namedtuple('User', ['id', 'username', 'password', 'role'])


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    auth = request.cookies.get('auth')
    user = pickle.loads(unhexlify(auth)) if auth else None
    return render_template('main.html', user=user)


@app.route('/articles')
def article_list():
    auth = request.cookies.get('auth')
    user = pickle.loads(unhexlify(auth)) if auth else None
    cur = get_db().cursor()
    articles = cur.execute('select * from articles').fetchall()
    return render_template('articles.html', articles=[Article(*art) for art in articles], user=user)


@app.route('/articles/<article_id>')
def single_article(article_id):
    auth = request.cookies.get('auth')
    user = pickle.loads(unhexlify(auth)) if auth else None
    cur = get_db().cursor()
    article = cur.execute('select * from articles where id={}'.format(article_id)).fetchone()
    return render_template('single_article.html', article=Article(*article), user=user)


@app.route('/articles/<article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    cur = get_db().cursor()
    if request.method == 'GET':
        auth = request.cookies.get('auth')
        user = None
        if auth:
            user = pickle.loads(unhexlify(auth))
        else:
            return redirect('/articles/{}'.format(article_id))
        article = cur.execute('select * from articles where id={}'.format(article_id)).fetchone()
        return render_template('edit_article.html', article=Article(*article), user=user)
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
        post_data = request.form
        username = post_data.get('username')
        password = post_data.get('password')

        if username and password:
            cur = get_db().cursor()
            m = md5()
            m.update(password.encode('utf8'))
            posted_pass_hash = m.hexdigest()

            user = User(*cur.execute('select * from users where username=\'{}\''.format(username)).fetchone())

            if posted_pass_hash == user.password:
                resp = redirect('/articles')
                response = app.make_response(resp)
                response.set_cookie('auth', hexlify(pickle.dumps(user)))
                return resp
        else:
            redirect('/login')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    resp = redirect('/')
    response = app.make_response(resp)
    response.set_cookie('auth', '', expires=0)
    return resp


@app.route('/users')
def user_list():
    auth = request.cookies.get('auth')
    # TODO: check role
    # 401 if not admin
    # 403 if not logged in

    if not auth:
        return redirect('/articles', 403)
    else:
        user = pickle.loads(unhexlify(auth))
        if user.role == 'admin':
            cur = get_db().cursor()
            users = cur.execute('select * from users').fetchall()
            return render_template('users.html', users=[User(*user) for user in users], user=user)
        else:
            return redirect('/articles', 401)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
