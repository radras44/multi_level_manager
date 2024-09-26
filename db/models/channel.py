from db.connection import Base
from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship,mapped_column,Mapped
from db.connection import Base
from typing import List
from db.models.associations.pathway_and_channel import pathway_and_channel_table

class Channel (Base) : 
    __tablename__ = "channel"
    
    id : Mapped[int] = mapped_column(primary_key=True) 
    guild : Mapped["Guild"] = relationship(back_populates="channels")
    guild_id : Mapped[int] = mapped_column(ForeignKey("guild.id"))
    pathways : Mapped[List["Pathway"]] = relationship(
        secondary=pathway_and_channel_table,
        back_populates="channels"
        )
    
    