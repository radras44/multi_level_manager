from sqlalchemy import Table,Column,ForeignKey
from db.connection import Base
guild_and_user_table = Table(
    "guild_and_user",
    Base.metadata,
    Column("guild_id",ForeignKey("guild.id"),primary_key=True),
    Column("user_id",ForeignKey("user.id"),primary_key=True)
)