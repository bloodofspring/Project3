import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template  # , redirect

import api
import database
from database.create import init_db
from database.models import UserProfile, AppUser

# from flask_login import LoginManager, login_user, login_required, logout_user

# from forms.job_form import JobForm

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
    five_unfollowed_dudes = []
    return render_template("main.html")


@application.route("/profile")
def profile_page():
    return render_template("profile.html")


# Пока что закомментирую (так сказать, до лучших времен)
# @application.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).filter(User.email == form.email.data).first()
#         if user and user.check_password(form.password.data):
#             login_user(user, remember=form.remember_me.data)
#             return redirect("/")
#         return render_template('login.html', message="Неправильный логин или пароль", form=form)
#     return render_template('login.html', title='Авторизация', form=form)


# @application.route('/add_job', methods=['GET', 'POST'])
# @login_required
# def add_job():
#     form = JobForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         job = Jobs()
#         job.job = form.job.data
#         job.team_leader = form.team_leader.data
#         job.work_size = form.work_size.data
#         job.collaborators = form.collaborators.data
#         job.is_finished = form.is_finished.data
#         db_sess.add(job)
#         db_sess.commit()
#         return redirect('/')
#     return render_template('add_job.html', title='Добавление работы', form=form)


# @application.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect("/")


def main():
    init_db()
    application.register_blueprint(api.blueprint)
    application.run(debug=True)


if __name__ == '__main__':
    main()
