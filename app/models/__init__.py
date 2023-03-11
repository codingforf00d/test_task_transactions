from gino import Gino
from sqlalchemy import Integer, Unicode, Column

db = Gino()


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    username = Column(Unicode(), nullable=False)
    password_hash = Column(Unicode(), nullable=False)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    # Постгря не умеет в unsigned, будем проверять эмаунт при вызове апи
    amount = Column(Integer(), nullable=False)
    from_user = Column(db.Integer(), db.ForeignKey('users.id'))
    to_user = Column(db.Integer(), db.ForeignKey('users.id'))
