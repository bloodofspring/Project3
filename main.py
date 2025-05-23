import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.utils import secure_filename
import random

import api
import database
import util
from database.create import init_db
from database.models import UserProfile, AppUser, FileMeta, Post, PostsToMedia, Comments

import logging

# from flask_login import LoginManager, login_user, login_required, logout_user


load_dotenv()

logging.basicConfig(level=logging.INFO)

application = Flask(__name__)
application.config['SECRET_KEY'] = os.environ["app_secret_key"]
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер загружаемых файлов
application.config['ALLOWED_EXTENSIONS'] = {".jpg", ".jpeg", ".png"}


@application.route("/")
@application.route("/main")
def main():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        user = AppUser.select().where(AppUser.login == session['user'])[0]
    except IndexError:
        return redirect(url_for("login"))

    if user.is_banned:
        return "Доступ запрещен. Ваш аккаунт заблокирован.", 403

    try:
        posts_from_user = Post.select().where(Post.author == user)
    except (Exception,) as e:
        print(f"Cannot get posts of user {user.login}: {e}")
        posts_from_user = []


    try:
        posts_from_other_users = Post.select().where(Post.author != user)
    except (Exception,) as e:
        posts_from_other_users = []
        print(f"Cannot get posts of user {user.login}: {e}")

    return render_template("main.html", user=user, posts_count=len(posts_from_user), posts=posts_from_other_users)


@application.route("/profile")
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        user = AppUser.select().where(AppUser.login == session['user'])[0]
    except IndexError:
        return redirect(url_for("login"))

    if user.is_banned:
        return "Доступ запрещен. Ваш аккаунт заблокирован.", 403

    return render_template("profile.html", user=user)


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
                file_meta: FileMeta | None = FileMeta(
                    path="static/images/",
                    filename="empty_profile",
                    extension="png",
                    size=3072,  # 3kb
                )

            user_data: UserProfile = UserProfile(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                profile_photo=file_meta,
                birth_date=datetime.datetime(
                    year=int(request.form['birth_date'].split("-")[0]) % 10000,
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

        if user[0].is_banned:
            return "Доступ запрещен. Ваш аккаунт заблокирован.", 403

        if user[0].password == util.hash_password(password):
            session['user'] = username
            print(f"Успешный вход, перенаправляю на {url_for('main')}")
            return redirect(url_for('main'))
        else:
            print("Неверный пароль")
            return render_template('login.html', error="Неверный логин или пароль")

    return render_template('login.html')


@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/save-about', methods=['POST'])
def save_about():
    about_text = request.form.get('about_text')

    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        user: AppUser = AppUser.select().where(AppUser.login == session['user'])[0]
    except IndexError:
        return redirect(url_for("login"))

    if user.is_banned:
        return "Доступ запрещен. Ваш аккаунт заблокирован.", 403

    with database.connect_to_database():
        user.profile_data.about = about_text
        user.profile_data.save()

    return redirect(url_for('profile'))


@application.route('/create_post', methods=['POST'])
def create_post():
    post_text = request.form.get('text', None)

    if request.files.get("photo"):
        photo = request.files.get("photo")

        if not os.path.exists("static/uploads"):
            os.mkdir("static/uploads")

        file_meta: FileMeta | None = FileMeta(
            path="static/uploads",
            extension=photo.filename.rsplit('.', 1)[1].lower(),
            size=-1,
        )

        photo.save(os.path.join("static/uploads", file_meta.filename + "." + file_meta.extension))
        file_meta.size = os.path.getsize(f"static/uploads/{file_meta.filename}.{file_meta.extension}")
    else:
        file_meta: FileMeta | None = None

    try:
        with database.connect_to_database():
            user = AppUser.select().where(AppUser.login == session["user"])[0]

            if user.is_banned:
                return "Доступ запрещен. Ваш аккаунт заблокирован.", 403

            new_post = Post(
                author=user,
                text=post_text,
            )
            new_post.save()

            if file_meta is not None:
                file_meta.save()
                PostsToMedia.create(
                    post=new_post,
                    media=file_meta
                )

            return redirect(url_for("main"))
    except IndexError:
        return redirect(url_for("login"))
    except Exception as e:
        print(f"Error creating post: {e}")
        return redirect(url_for("main"))


@application.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    text = data.get('text', None)

    if text is None:
        return redirect(url_for("main"))

    try:
        user = AppUser.select().where(AppUser.login == session["user"])[0]

        if user.is_banned:
            return "Доступ запрещен. Ваш аккаунт заблокирован.", 403

        post = Post.get_by_id(data.get('post_id'))
        if not post:
            raise Exception("Post not found")

        Comments.create(
            post=post,
            author=user,
            text=text,
        )
    except Exception as e:
        print(f"An error while creating comment: {e}")
        return redirect(url_for("main"))

    return redirect(url_for("main"))


def run():
    init_db()
    application.register_blueprint(api.blueprint)
    application.run(debug=True)


if __name__ == '__main__':
    run()
