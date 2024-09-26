from db.connection import Base
from sqlalchemy import Column,Integer,String,ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship,mapped_column,Mapped
from db.connection import Base
from typing import List

class Role (Base) : 
    __tablename__ = "role"
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    discord_id : Mapped[int] = mapped_column(nullable=False)
    level : Mapped[int] = mapped_column(nullable=False)
    pathway : Mapped["Pathway"] = relationship(back_populates="roles")
    pathway_id : Mapped[int] = mapped_column(ForeignKey("pathway.id"))
    pathway_exp_refs: Mapped[List["Pathway_exp_ref"]] = relationship(back_populates="role")
    
    __table_args__ = (
        UniqueConstraint("discord_id","pathway_id",name="discordid_pathwayid_uc"),
        UniqueConstraint("level","pathway_id",name="level_pathwayid_uc")
    )
    
        