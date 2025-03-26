from datetime import datetime

from peewee import Model, AutoField, DateTimeField

from database import connect_to_database


class BaseModel(Model):
    """
    Базовая модель с автоматическим заполнением поля ID и сохранением времени создания, изменения
    """
    id = AutoField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = connect_to_database()
