import discord
import os
from dotenv import load_dotenv
from commands.pathway_manager.pathway_manager import Pathway_manager
from commands.task_manager.level_manager import Level_manager
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db.models.guild import Guild
from db.seed.seeder import main_seeder
from db.config import create_tables
from db import connection
load_dotenv()

def main () : 
    create_tables()
    bot = discord.Bot(intents = discord.Intents.all())
    @bot.event
    async def on_ready():
        print("bot ready...")
    
    @bot.slash_command()
    async def role_list(ctx) : 
        roles = [(role.name, role.id) for role in ctx.guild.roles]
        message = ""
        for role_name,role_id in roles : 
            message += f"{role_name} - id: {role_id}\n"
        await ctx.respond(f"```\n{message}\n```")
    
    @bot.slash_command()
    async def register_guild (ctx : discord.ApplicationContext) : 
        try:
            session = connection.Session()
            new_guild = Guild(
                id=ctx.guild_id,
                )
            session.add(new_guild)
            session.commit()
            await ctx.respond(f"Servidor {ctx.guild.name} registrado con éxito")
        except IntegrityError :
            await ctx.respond(f"Este servidor ya se encuentra registrado")
        finally :
            session.close()
   
        
    token = os.getenv("BOT_TOKEN")
    if not token : 
        raise ValueError("token missing")

    bot.add_cog(Pathway_manager(bot=bot))
    bot.add_cog(Level_manager(bot=bot))
    bot.run(token)
     
if __name__ == "__main__" : 
    main()
