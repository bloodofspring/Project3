import json
import os

import flask

import database
import util
from database.models import Post, AppUser, FileMeta, PostsToMedia

blueprint = flask.Blueprint(
    'site_api',
    __name__,
    template_folder='templates',
    url_prefix="/api"
)


@blueprint.route('/get_post')
def get_post():
    """
    Получить пост из бд
    :return:
    """

    post_id = flask.request.args.get("post_id")
    if post_id is None:
        return json.dumps({"message": "You should pass param post_id to get post by id"}), 400

    try:
        post_id = int(post_id)
    except (Exception,):
        return json.dumps({"message": "post_id should be a number"}), 422

    with database.connect_to_database():
        posts = Post.select().where(Post.id == post_id)[:]
        if len(posts) == 0:
            return json.dumps({"message": f"Post with ID {post_id} does not exist"}), 404

    try:
        max_comments = flask.request.args.get('max_comments')
        show_max_replies = flask.request.args.get('show_max_replies')

        if max_comments is not None:
            max_comments = int(max_comments)

        if show_max_replies is not None:
            show_max_replies = int(show_max_replies)
    except (Exception,):
        return json.dumps({"message": "Invalid datatype"}), 400

    return posts[0].json(
        max_comments=max_comments,
        show_max_replies=show_max_replies,
    ), 201


@blueprint.route('/get_user')
def get_user():
    """
    Получить пользователя из бд
    :return:
    """
    username = flask.request.args.get("username")
    if username is None:
        return json.dumps({"message": "You should pass param username to get user"}), 400

    with database.connect_to_database():
        users = AppUser.select().where(AppUser.login == username)[:]

        if len(users) == 0:
            return json.dumps({"message": f"User with login {username} does not exist"}), 404

    return users[0].json(), 201


@blueprint.route('/download_media')
def download_media():
    """
    Получить медиа
    :return:
    """

    file_id = flask.request.args.get("file_id")
    if file_id is None:
        return json.dumps({"message": "You should pass param file_id to download file"}), 400

    with database.connect_to_database():
        files = FileMeta.select().where(FileMeta.filename == file_id)[:]

        if len(files) == 0:
            return json.dumps({"message": f"File with file_id={file_id} does not exist"}), 404

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
        ), 201

    except FileNotFoundError:
        return json.dumps({"message": "File not found"}), 404
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")

        return json.dumps({"message": "An error occurred while processing your request."}), 500

    return None


@blueprint.route('/upload_post', methods=["POST"])
def upload_post():
    """
    Опубликовать пост
    :return:
    """
    login = flask.request.form.get('login')
    password = flask.request.form.get('password')
    text = flask.request.form.get('text')
    files = flask.request.files.getlist('files')

    if login is None:
        return json.dumps({"message": "Username not specified (login)"}), 401

    if password is None:
        return json.dumps({"message": f"No password specified for user {login} (password)"}), 401

    if not util.authenticate(login, password):
        return json.dumps({'message': 'A non-existent user or incorrect password was specified.'}), 401

    if not text and not files:
        return json.dumps({'message': 'The post requires text or media'}), 400

    if len(files) > 5:  # ToDo: Вынести ограничения в отдельный файл конфигурации
        return json.dumps({"message": "You cannot post more than 5 files at once"}), 400

    save_results = []
    allowed_post_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

    if not os.path.exists("static/posts"):
        os.mkdir("static/posts")

    if not os.path.exists("static/posts/post_media"):
        os.mkdir("static/posts/post_media")

    for file in files:
        if not file:
            continue

        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_post_extensions:
            save_results.append({
                "src_filename": file.filename,
                "verdict": "incorrect extension",
                "meta": None,
            })

            continue

        with database.connect_to_database():
            file_meta = FileMeta.create(
                path="static/posts/post_media",
                extension=file.filename.rsplit('.', 1)[1].lower(),
                size=-1,
            )
            file.save(os.path.join("static/posts/post_media", file_meta.filename + "." + file_meta.extension))
            file_meta.size = os.path.getsize(f"static/posts/post_media/{file_meta.filename}.{file_meta.extension}")
            file_meta.save()
            save_results.append({
                "src_filename": file.filename,
                "verdict": "saved",
                "meta": file_meta
            })

    try:
        with database.connect_to_database():
            author = AppUser.select().where(AppUser.login == flask.request.form.get('login'))[0]

            if author.is_banned:
                return "Доступ запрещен. Ваш аккаунт заблокирован.", 403

            post = Post.create(
                author=author,
                text=flask.request.form.get('text')
            )

            for f in map(lambda x: x["meta"], save_results):
                if f is None:
                    continue

                PostsToMedia.create(
                    post=post,
                    media=f,
                )

    except Exception as e:
        print(e)

        return json.dumps({"message": "An error occurred while processing your request."}), 500

    for e in save_results:
        if e["meta"] is None:
            continue

        e["meta"] = e["meta"].dict()

    response_data = {
        'message': 'The post has been successfully published!',
        'username': login,
        'text': text,
        'uploaded_files': save_results,
    }

    return json.dumps(response_data), 201
