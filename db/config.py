from db.models.guild import Guild
from db.models.pathway import Pathway
from db.models.role import Role
from db.models.channel import Channel
from db.models.user import User
from db.models.pathway_exp_ref import Pathway_exp_ref
from db.connection import Base,engine
def create_tables () : 
    Base.metadata.create_all(engine)
