from db.connection import Base
from sqlalchemy import ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship,mapped_column,Mapped
from db.connection import Base
from typing import List
from db.models.associations.pathway_and_channel import pathway_and_channel_table
class Pathway (Base) : 
    __tablename__ = "pathway"
    
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name : Mapped[str] = mapped_column(nullable=False)
    exp_cooldown : Mapped[int] = mapped_column(nullable=False)
    
    guild : Mapped["Guild"] = relationship(back_populates="pathways")
    guild_id : Mapped[int] = mapped_column(ForeignKey("guild.id"))
    roles : Mapped[List["Role"]] = relationship(
        back_populates="pathway",
        cascade="all,delete"
    )
    pathway_exp_refs : Mapped[List["Pathway_exp_ref"]] = relationship(back_populates="pathway",cascade="all,delete")
    channels : Mapped[List["Channel"]] = relationship(
        secondary=pathway_and_channel_table,
        back_populates="pathways"
    )
    
    __table_args__ = (
        UniqueConstraint("guild_id","name",name="_guildid_name_uc"),
    )
    
