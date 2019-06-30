from peewee import *
from datetime import datetime, timedelta


database = SqliteDatabase('./lobbies.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0})


class Lobby(Model):
    id = BigAutoField()
    subject = CharField()
    author = CharField()
    author_mention = CharField()
    server = IntegerField()
    slots = IntegerField()
    created = DateTimeField(default=datetime.now())

    class Meta:
        database = database
        table_name = "lobby"
        pass
    pass


class LobbyList(Model):
    id = BigAutoField()
    lobby = ForeignKeyField(Lobby, backref='user', null=True)
    user = CharField()
    user_mention = CharField()
    joined = DateTimeField(default=datetime.now())

    class Meta:
        database = database
        table_name = "lobby_list"
    pass


def check_db():
    if not Lobby.table_exists():
        Lobby.create_table()
    if not LobbyList.table_exists():
        LobbyList.create_table()
        pass
    pass
