import json
import os

import flask

import database
from database.models import Post, AppUser, FileMeta

blueprint = flask.Blueprint(
    'site_api',
    __name__,
    template_folder='templates',
    url_prefix="/api"
)


@blueprint.route('/download_post/<int:post_id>')
def get_post(post_id: int):
    """
    Получить пост из бд
    :param post_id:
    :return:
    """
    with database.connect_to_database():
        posts = Post.select().where(Post.id == post_id)[:]
        if len(posts) == 0:
            return json.dumps({
                "error": True,
                "code": 404,
                "message": f"Поста с ID {post_id} не существует"
            })

    return posts[0].json(
        max_comments=flask.request.form.get('max_comments'),
        show_max_replies=flask.request.form.get('show_max_replies'),
    )


@blueprint.route('/get_user/<str:username>')
def get_post(username: str):
    """
    Получить пользователя из бд
    :param username:
    :return:
    """
    with database.connect_to_database():
        users = AppUser.select().where(AppUser.login == username)[:]

        if len(users) == 0:
            return json.dumps({
                "error": True,
                "code": 404,
                "message": f"Пользователя с логином {username} не существует"
            })

    return users[0].json()

@blueprint.route('/download_media/<str:file_id>')
def get_post(file_id: str):
    """
    Получить медиа
    :param file_id:
    :return:
    """

    with database.connect_to_database():
        files = FileMeta.select().where(FileMeta.filename == file_id)

        if len(file_id) == 0:
            return json.dumps({
                "error": True,
                "code": 404,
                "message": f"Файла с file_id={files} не существует"
            })

    file_db = files[0]

    try:
        file_path = os.path.join(flask.current_app.root_path, file_db.get_full_path())

        if not os.path.isfile(file_path):
            flask.abort(404)

        return flask.send_file(
            file_path,
            as_attachment=True,
            download_name=f"file_{file_db.filename}.{file_db.extension}",
            mimetype='text/plain',
        )

    except FileNotFoundError:
        return json.dumps({
            "error": True,
            "code": 404,
            "message": "Файл не найден"
        })
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")

        return json.dumps({
            "error": True,
            "code": 500,
            "message": "Произошла ошибка при обработке запроса"
        })

    return None

# ToDo: Реализовать
# @blueprint.route('/api/post/<int:post_id>')
# def get_post(post_id: int):
#     """
#     Опубликовать пост
#     :param post_id:
#     :return:
#     """
#     return json.dumps({
#         "address": f"/api/post/{post_id}",
#         "post_id": post_id,
#     })

