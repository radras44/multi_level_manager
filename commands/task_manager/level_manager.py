from discord.ext import commands,tasks
import discord
from typing import List
from db.models.channel import Channel
from db.models.pathway_exp_ref import Pathway_exp_ref
from db.models.pathway import Pathway
from db.models.guild import Guild
from db.models.role import Role
import traceback
import io
import base64
from db.models.user import User
from db.models.associations.pathway_and_channel import pathway_and_channel_table
from discord.utils import get
from typing import Optional
from commands.utils.error_embed import error_embed
from PIL import Image,ImageDraw
from sqlalchemy import select,update
from sqlalchemy.orm import selectinload
from uuid import uuid4
import db.connection as connection
import time
class Level_manager (commands.Cog) :
    def __init__ (self,bot) : 
        self.xp_rate = 10
        self.increment_coef = 1.02
        self.lvl_1_xp = 100
    
    def xp_to_level (self,xp) : 
        current_xp = int(xp)
        lvl = 0
        xp_acc = self.lvl_1_xp
        while xp > xp_acc : 
            xp -= xp_acc
            lvl += 1
            xp_acc *= self.increment_coef
        return int(lvl),int(xp),int(current_xp + (xp_acc - xp))
    
    def gen_xp_bar (self,perc : float) -> str :
        w,h = 400,10
        center = int(h/2)-1 
        color="#fbc02d"
        background = "#ff6f00"
        image = Image.new("RGBA",(w,h),color=background)
        draw = ImageDraw.Draw(image)
        draw.line((0,center,int(w*perc),center),fill=color,width=h)
        buffered = io.BytesIO()
        image.save(buffered,format="PNG")
        buffered.seek(0)
        return buffered   
    
    @discord.slash_command()
    async def test (self,ctx : discord.ApplicationContext) : 
        print("roles:_____________________________\n",ctx.author.roles)
        await ctx.respond("respondd")
    
    @discord.slash_command()
    async def xp (self,ctx : discord.ApplicationContext,user : discord.User | None = None) :  
        session = connection.Session()
        try : 
            channel = session.execute(
                select(Channel)
                .where(Channel.id == ctx.channel_id)
            ).scalar_one_or_none()

            if channel is None or len(channel.pathways) <= 0 : 
                await ctx.respond(embed=discord.Embed(title="No disponible",description="No hay rutas asociadas a este canal"))
                return
            
            pathway_ids = [pathway.id for pathway in channel.pathways]
            
            user_id = user.id if user else ctx.user.id
            xp_refs : List[Pathway_exp_ref] = session.execute(
                select(Pathway_exp_ref)
                .where(
                    Pathway_exp_ref.user_id == user_id,
                    Pathway_exp_ref.pathway_id.in_(pathway_ids)
                )
            ).scalars().all()
            print("pathways:____________\n",xp_refs)
            embeds = [] 
            files : List[discord.File]= []
            for xp_ref in xp_refs : 
                lvl,xp_rest,xp_next = self.xp_to_level(xp_ref.value)
                perc : float = xp_rest / ((xp_next - xp_ref.value) + xp_rest)
                img_buffer = self.gen_xp_bar(perc)
                filename = f"{xp_ref.id}.png"
                file = discord.File(img_buffer,filename=filename)
                files.append(file)
                embed = discord.Embed(
                    title=xp_ref.pathway.name
                )
                embed.add_field(name="Rol",value=get(ctx.guild.roles,id=xp_ref.role.discord_id) if xp_ref.role else "Sin rol")
                embed.add_field(name="level",value=lvl)
                embed.add_field(name="XP",value=f"{xp_ref.value} / {xp_next}")
                embed.add_field(name="perc",value=str(round(perc * 100,1))+"%")
                embed.set_image(url=f"attachment://{filename}")
                embeds.append(embed)
            if len(embeds) > 0:
                await ctx.respond(embeds=embeds,files=files)
            else :
                await ctx.respond("no se han encontrado registros de experiencia para ninguna ruta asociada a este chat")
        except Exception as e : 
            print(e)
            await ctx.respond(embed=error_embed(e))
        finally : session.close()
    
    @discord.slash_command()
    async def set_xp (self,ctx : discord.ApplicationContext,user : discord.User ,pathway_name : str,xp_value: int) :
        session = connection.Session()
        level,_,_ = self.xp_to_level(xp_value)
        try :
            session.execute(
                update(Pathway_exp_ref)
                .where(
                    Pathway_exp_ref.pathway_id == (select(Pathway.id).where(Pathway.name == pathway_name).scalar_subquery()),
                    Pathway_exp_ref.user_id == user.id
                )
                .values(
                    value=xp_value,
                    level=level
                )
            ).scalar_one_or_none() 
            session.commit()
            embed = discord.Embed(
                title="Usuario actualizado con éxito"
            )
            embed.add_field(name="nivel",value=str(level))
            embed.add_field(name="xp",value=str(xp_value))
            await ctx.respond(embed=embed)
        except Exception as e :
            print(e)
            await ctx.respond(embed=error_embed(e))
        finally : session.close()
    
    @discord.slash_command()
    async def test (self,ctx:discord.ApplicationContext,name : str,user:discord.User) :
        guild : discord.Guild = ctx.guild
        member = guild.get_member(user.id)
        role = get(ctx.guild.roles,name=name)
        if role : 
            await member.add_roles(role) 
        await ctx.respond(f"rol asignado con exito")
        
             
    @discord.Cog.listener("on_message")
    async def on_message (self,message:discord.Message) : 
        start_time = time.time()
        session = connection.Session()
        user_id = message.author.id
        
        guild_id = message.guild.id
        try:
            user = session.execute(
               select(User)
               .where(User.id == user_id)
            ).scalar_one_or_none()
            if user is None :
                new_user = User(
                    id=user_id
                    )
                guild = Guild(id=guild_id)
                marge_guild = session.merge(guild)
                new_user.guilds.append(marge_guild)
                session.add(new_user)
                session.commit()
                user = new_user
                
            pathways =  session.execute(
               select(Pathway.id,Role.discord_id,Role.level,Pathway.exp_cooldown,Role.id)
               .outerjoin(Channel.pathways)
               .outerjoin(Pathway.roles)
               .where(Channel.id == message.channel.id)
            ).all()
 
            if len(pathways) <= 0 : 
                return   
            
            pathway_objs = {}
            for row in pathways : 
                id,discord_id,level,cooldown,role_id = row
                if role_id is None : 
                    pathway_objs[id] = {
                        "cooldown" : cooldown,
                        "roles" : []
                    }
                    continue
                if row[0] in pathway_objs : 
                    pathway_objs[id]["roles"].append({"discord_id" :discord_id,"level" :level})
                else : 
                    pathway_objs[id] = {
                        "cooldown" : cooldown,
                        "roles" : [
                            {"discord_id" :discord_id,"level" :level,"id":role_id}
                        ]
                    }
                    
      
            
            for pathway_id in pathway_objs :
                pathway = pathway_objs[pathway_id] 
                pathway_exp_ref = session.execute(
                    select(Pathway_exp_ref)
                    .where(
                        Pathway_exp_ref.pathway_id == pathway_id,
                        Pathway_exp_ref.user_id == message.author.id
                           )
                ).scalar_one_or_none()
                if pathway_exp_ref is None :
                    new_ref = Pathway_exp_ref(
                        value = self.xp_rate,
                        last_update = time.time(),
                        pathway_id = pathway_id,
                        level = 0,
                        user_id = user.id
                    )
                    session.add(new_ref)
                    session.commit()
                    pathway_exp_ref = new_ref
                    return
                                
                now = time.time() 
                if now - pathway_exp_ref.last_update >= pathway["cooldown"] : 
                    new_xp = pathway_exp_ref.value + self.xp_rate
                    level,_,_ = self.xp_to_level(new_xp)
                    new_role = None
                    if pathway["roles"] : 
                        upper_roles_to_remove = []
                        pathway_roles :List[Role] =sorted(pathway["roles"],key=lambda rol:rol["level"],reverse=True)
                        for role in pathway_roles : 
                            if level >= role["level"] :
                                role_obj = get(message.guild.roles,id=role["discord_id"]) 
                                new_role = role
                                await message.author.add_roles(role_obj) 
                                break
                            else : 
                                upper_roles_to_remove.append(get(message.guild.roles,id=role["discord_id"]))
                      
                        if (
                            (new_role is None and pathway_exp_ref.role) or 
                            (new_role and pathway_exp_ref.role and new_role["discord_id"] != pathway_exp_ref.role.discord_id)
                        ): 
                            print("eliminando rol guardado antes del update...")
                            upper_roles_to_remove.append(get(message.guild.roles,id=pathway_exp_ref.role.discord_id))
                        print(f"eliminando lo siguientes roles : \n{upper_roles_to_remove}")
                        await message.author.remove_roles(*upper_roles_to_remove)  

                         
                    session.execute(
                        update(Pathway_exp_ref)
                        .where(Pathway_exp_ref.id == pathway_exp_ref.id)
                        .values(
                            value=new_xp,
                            level=level,
                            role_id = new_role["id"] if new_role else None,
                            last_update = now
                        )
                    )
            session.commit() 
        except Exception as e : 
            print(f"Error: {type(e).__name__} - {e}")
            traceback.print_exc()
        finally : 
            session.close()
            end_time = time.time()
            print(f"task operation time => {end_time - start_time}s")