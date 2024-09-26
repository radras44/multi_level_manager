from db.connection import Base
from sqlalchemy import ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
class Pathway_exp_ref (Base) :
    __tablename__ = "pathway_exp_ref"
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    value : Mapped[int] = mapped_column(nullable=False)
    level : Mapped[int] = mapped_column(nullable=False)
    last_update : Mapped[float] = mapped_column(nullable=False)
    user_id : Mapped[int] = mapped_column(ForeignKey("user.id"))
    user : Mapped["User"] = relationship(back_populates="pathway_exp_refs")
    role_id : Mapped[int] = mapped_column(ForeignKey("role.id"),nullable=True)
    role : Mapped["Role"] = relationship(back_populates="pathway_exp_refs")
    pathway_id : Mapped[int] = mapped_column(ForeignKey("pathway.id"))
    pathway : Mapped["Pathway"] = relationship(back_populates="pathway_exp_refs")
    
    __table_args__ = (
        UniqueConstraint("user_id","pathway_id",name="_userid_pathwayid_uc"),
    )
    