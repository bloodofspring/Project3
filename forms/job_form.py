from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class JobForm(FlaskForm):
    job = StringField("Team leader id", validators=[DataRequired()], render_kw={"placeholder": "search for water on the surface"})
    team_leader = IntegerField("Team leader id", validators=[DataRequired()], render_kw={"placeholder": "2"})
    work_size = IntegerField("Work Size", validators=[DataRequired()], render_kw={"placeholder": "20"})
    collaborators = StringField("Collaborators", validators=[DataRequired()], render_kw={"placeholder": "5, 7"})
    is_finished = BooleanField("Is job finished")
    submit = SubmitField("Добавить работу")
