import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, session


import api
import database
from database.create import init_db
from database.models import UserProfile, AppUser

# from flask_login import LoginManager, login_user, login_required, logout_user


load_dotenv()

application = Flask(__name__)
application.config['SECRET_KEY'] = os.environ["app_secret_key"]
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер загружаемых файлов

# login_manager = LoginManager()
# login_manager.init_app(application)


# @login_manager.user_loader
# def load_user(user_id):
#     db_sess = db_session.create_session()
#     return db_sess.query(User).get(user_id)


@application.route("/")
def index():
    return render_template("index.html")


@application.route("/main")
def main_page():
    user = ...
    five_unfollowed_dudes = ['Johny Depp', 'Elon Musk', 'bloodofspring', 'SIlD', 'GodGamer228']
    return render_template("main.html", dudes=five_unfollowed_dudes)


@application.route("/profile")
def profile_page():
    return render_template("profile.html")


users_db = {
    # Пример пользователя:
    "test_user": {
        "first_name": "Иван",
        "last_name": "Иванов",
        "birth_date": "1990-01-01",
        "email": "ivan@example.com",
        "password": "12345"  # Пароли должны храниться в хешированном виде!
    }
}


@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Получаем данные из формы
        user_data = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "birth_date": request.form['birth_date'],
            "email": request.form['email'],
            "username": request.form['username'],
            "password": request.form['password']  # ToDo: захэшировать пароли
        }

        # Проверка на занятось логина или почты
        if user_data['username'] in users_db:
            return render_template('register.html', error="Логин уже занят")
        if any(u['email'] == user_data['email'] for u in users_db.values()):
            return render_template('register.html', error="Почта уже используется")

        # ToDo: Сохрани пользователя в БД)
        users_db[user_data['username']] = user_data
        return redirect(url_for('login'))

    return render_template('register.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_db.get(username)

        if user and user['password'] == password:
            session['user'] = username
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error="Неверный логин или пароль")

    return render_template('login.html')


@application.route('/success')
def success():
    return "Регистрация прошла успешно!"


def main():
    init_db()
    application.register_blueprint(api.blueprint)
    application.run(debug=True)


if __name__ == '__main__':
    main()
