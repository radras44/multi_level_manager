from db.connection import Base
from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import relationship,mapped_column,Mapped
from db.models.associations.guild_and_user import guild_and_user_table
from db.connection import Base
from typing import List

class Guild (Base) : 
    __tablename__ = "guild"
    
    id : Mapped[int] = mapped_column(primary_key=True)
    
    pathways : Mapped[List["Pathway"]] = relationship(back_populates="guild",cascade="all,delete")
    channels : Mapped[List["Channel"]] = relationship(back_populates="guild",cascade="all,delete")
    users : Mapped[List["User"]] = relationship(
        back_populates="guilds",
        secondary=guild_and_user_table,
        cascade="all,delete"
        )
    

    