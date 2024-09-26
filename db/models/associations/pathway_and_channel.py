from sqlalchemy import Table,Column,ForeignKey
from db.connection import Base
pathway_and_channel_table = Table(
    "pathway_and_channel",
    Base.metadata,
    Column("pathway_id",ForeignKey("pathway.id"),primary_key=True),
    Column("channel_id",ForeignKey("channel.id"),primary_key=True)
)