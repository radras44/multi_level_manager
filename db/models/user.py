from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from db.connection import Base
from db.models.associations.guild_and_user import guild_and_user_table
from typing import List
class User (Base): 
    __tablename__ = "user"
    id : Mapped[int] = mapped_column(primary_key=True,nullable=False)
    guilds : Mapped[List["Guild"]] = relationship(
        back_populates="users",
        secondary=guild_and_user_table
    )
    pathway_exp_refs : Mapped[List["Pathway_exp_ref"]] = relationship(back_populates="user",cascade="all,delete")
    
    