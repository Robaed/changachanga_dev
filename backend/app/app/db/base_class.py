import hmac
import random
import string
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

from app.utils import camel2snake


def general_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def number_id_generator(size=6, chars=string.digits[1:]):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def generate_unique_str() -> str:
    s = uuid.uuid4()
    return str(s)


def generate_hash_sequence():
    try:
        from hashlib import sha1
    except ImportError:
        import sha
        sha1 = sha.sha
    new_uuid = uuid.uuid4()
    new_key = hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()
    return new_key


def generate_random_sequence(
        connection,
        table,
        column_id,
        generator_type='number',
        prefix='',
        number_size=6,
        general_size=10
):
    """
    Generates a new random number sequence.Retries if sequeces
    already exists in model.
    Args:
        table: parent model
        column_id: where sequence is stored.
    """
    random_number = None
    if generator_type == 'general':
        random_number = general_id_generator(size=general_size)
    elif generator_type == 'hash':
        random_number = generate_hash_sequence()
    else:
        random_number = number_id_generator(size=number_size)
    random_number = '%s%s' % (prefix, random_number)
    column_name = table.name + "." + column_id
    for c in table.columns:
        if str(c) == column_name:
            column_name = c
    number_ex = connection.execute(
        table.select().where(column_name == random_number)
    ).scalar()
    if number_ex:
        return generate_random_sequence(connection, table, column_id, generator_type)
    return random_number


class Base(AsyncAttrs, DeclarativeBase):
    id: Any

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return camel2snake(f"{cls.__name__}s")


class AutoIdColumns:
    id: Mapped[str] = mapped_column(default=generate_unique_str, index=True, primary_key=True)


class AuditColumns:
    created_date_utc: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_by: Mapped[str| None]
    last_edited_date_utc: Mapped[datetime] = mapped_column(onupdate=datetime.utcnow)
    last_edited_by: Mapped[str | None] = mapped_column(String(200) )
    is_deleted: Mapped[bool] = mapped_column(default=False)

    @classmethod
    def __declare_last__(cls):
        # get called after mappings are completed
        # http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html#declare-last
        event.listen(cls, 'before_insert', cls.audit_columns_before_insert)
        event.listen(cls, 'before_update', cls.audit_columns_before_update)

    @staticmethod
    def audit_columns_before_insert(mapper, connection, target):
        target.last_edited_date_utc = datetime.utcnow()

    @staticmethod
    def audit_columns_before_update(mapper, connection, target):
        target.last_edited_date_utc = datetime.utcnow()
