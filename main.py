import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, session, flash


import api
import database
import util
from database.create import init_db
from database.models import UserProfile, AppUser, FileMeta

import logging

# from flask_login import LoginManager, login_user, login_required, logout_user


load_dotenv()

logging.basicConfig(level=logging.INFO)

application = Flask(__name__)
application.config['SECRET_KEY'] = os.environ["app_secret_key"]
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер загружаемых файлов
application.config['ALLOWED_EXTENSIONS'] = {".jpg", ".jpeg", ".png"}

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
def main():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        user = AppUser.select().where(AppUser.login == session['user'])[0]
    except IndexError:
        return f"Пользователя с ником {session['user']} не существует", 404

    five_unfollowed_dudes = ['Johny Depp', 'Elon Musk', 'bloodofspring', 'SIlD', 'GodGamer3000']
    return render_template("main.html", dudes=five_unfollowed_dudes, user=session['user'])


@application.route("/profile")
def profile_page():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template("profile.html")


@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        with database.connect_to_database():
            if request.files.get("avatar"):
                avatar = request.files.get("avatar")

                if not os.path.exists("static/users"):
                    os.mkdir("static/users")

                if not os.path.exists("static/users/profile_photos"):
                    os.mkdir("static/users/profile_photos")

                file_meta: FileMeta | None = FileMeta(
                    path="static/users/profile_photos",
                    extension=avatar.filename.rsplit('.', 1)[1].lower(),
                    size=-1,
                )

                avatar.save(os.path.join("static/users/profile_photos", file_meta.filename + "." + file_meta.extension))
                file_meta.size = os.path.getsize(f"static/users/profile_photos/{file_meta.filename}.{file_meta.extension}")
            else:
                file_meta: FileMeta | None = None

            user_data: UserProfile = UserProfile(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                profile_photo=file_meta,
                birth_date=datetime.datetime(
                    year=int(request.form['birth_date'].split("-")[0]),
                    month=int(request.form['birth_date'].split("-")[1]),
                    day=int(request.form['birth_date'].split("-")[2]),
                ),
            )

            current_user: AppUser = AppUser(
                email=request.form['email'].lower(),
                # email_is_hidden=False,
                login=request.form['username'].lower(),
                password=util.hash_password(request.form['password']),
                profile_data=user_data,
            )

            users_with_same_username = AppUser.select().where(AppUser.login == current_user.login)[:]

            if len(users_with_same_username) != 0:
                return render_template('register.html', error="Логин уже занят")

            users_with_same_email = AppUser.select().where(AppUser.email == current_user.email)[:]

            if len(users_with_same_email) != 0:
                return render_template('register.html', error="Почта уже используется")

            try:
                if file_meta:
                    file_meta.save()

                user_data.save()
                current_user.save()
            except (Exception,) as registration_error:
                logging.warning(
                    f"При регистрации пользователя {AppUser.login} ({AppUser.email}) произошла ошибка! "
                    f"({type(registration_error)}: {registration_error})"
                )

        return redirect(url_for('login'))

    return render_template('register.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        user: list[AppUser] = AppUser.select().where(AppUser.login == username)[:]

        if len(user) == 0:
            print("Пользователь не найден")
            return render_template('login.html', error="Неверный логин или пароль")

        if user[0].password == util.hash_password(password):
            session['user'] = username
            print(f"Успешный вход, перенаправляю на {url_for('main')}")
            return redirect(url_for('main'))
        else:
            print("Неверный пароль")
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
