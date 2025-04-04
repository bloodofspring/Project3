import json

import flask

blueprint = flask.Blueprint(
    'site_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/post/<int:post_id>')
def get_post(post_id: int):
    return json.dumps({
        "address": f"/api/post/{post_id}",
        "post_id": post_id,
    })
