import os
import json
from sqlalchemy.orm import Session
from db.models.guild import Guild
from sqlalchemy.exc import IntegrityError
def main_seeder (session : Session) :
    with open(os.path.join("db","seed","mocks","MOCK_DATA.json")) as f :
        guild_objs = json.load(f)
        
    for obj in guild_objs : 
        session.add(Guild(id=obj["id"],name=obj["name"]))
        
    try :
        session.commit()
        print("seeders aplicados")
    except IntegrityError : 
        print("seedes ya aplicados"),
    except Exception as e :
        print("error desconocido, no se ha podido aplicar el seeder\n",e)
     
    session.close()
        
    