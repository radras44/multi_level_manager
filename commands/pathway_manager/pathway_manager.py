from discord.ext import commands
from discord import default_permissions
from commands.pathway_manager.views.add_role import Pathway_add_role_view
from commands.pathway_manager.views.select_pathway_channel_view import Select_pathway_channel_view
from commands.pathway_manager.views.v_select_role import V_select_role
from commands.pathway_manager.views.v_select_pathway_roles import V_select_pathway_roles
from db.models.channel import Channel
from sqlalchemy import select,update,delete
from sqlalchemy.orm import Session
from typing import List
from commands.views.delete_name_confirmation import Delete_name_confirmation
from commands.utils.error_embed import error_embed
from sqlalchemy.exc import IntegrityError,ConstraintColumnNotFoundError
from db.models.pathway import Pathway
from db.models.role import Role
from db import connection
from uuid import uuid4
from discord.utils import get
import discord

class Pathway_manager (commands.Cog) :
    def __init__ (self,bot) : 
        self.bot = bot
    
    @commands.slash_command(name="pathway_list",description="Obtener una lista con las rutas disponibles en el servidor y sus roles afiliados")
    async def pathway_list (self,ctx : discord.ApplicationContext) : 
        session = connection.Session()
        try : 
            res = session.execute(
                select(Pathway).filter_by(guild_id = ctx.guild_id)
            ).all()
            embed = discord.Embed(title="Rutas:")
            if len(res) <= 0 : 
                await ctx.respond(embed=discord.Embed(
                title="No encontrado",
                description="No se han encontrado rutas en este servidor"
                ))
                return 
            
            for result in res : 
                pathway = result[0]
                embed.add_field(name=pathway.name,value=pathway.id,inline=True)
                
            await ctx.respond(embed=embed)
            
        except Exception as e : await ctx.respond(embed=error_embed(e))
        finally : session.close() 
        
    @commands.slash_command()    
    async def pathway_info (self,ctx:discord.ApplicationContext,name) : 
        session = connection.Session()
        try : 
            pathway = await self.handle_missing_pathway(session,ctx,name)
            if pathway is None : return
            embed = discord.Embed(title=pathway.name)
            embed.add_field(name="enfriamiento de aumento de experiencia",value=f"{pathway.exp_cooldown} segundos",inline=False)
            if len(pathway.roles) <= 0 :
                embed.add_field(name="Roles",value="aun no se le han asignado roles a esta ruta")
            else : 
                roles : List[Role] = sorted(pathway.roles,key=lambda r: r.level)
                values = "\n".join([f"nivel {role.level} => {get(ctx.guild.roles,id=role.discord_id).name}" for role in roles])
                embed.add_field(name="Roles",value=values,inline=False)
                
            if len(pathway.channels) <= 0 :
                embed.add_field(name="Canales asociados",value="Esta ruta no esta asociada a ningún canal")
            else : 
                values = "\n".join([f"#{get(ctx.guild.channels,id=int(channel.id))}" for channel in pathway.channels])
                embed.add_field(name="Canales asociados",value=values,inline=False)

            
            await ctx.respond(embed=embed)
            
        except Exception as e : await ctx.respond(embed=error_embed(e))
        
        
    @commands.slash_command()
    @default_permissions(manage_roles=True)
    async def pathway_create (self,ctx : discord.ApplicationContext,name : str) : 
        async def handleSubmit (interaction : discord.Interaction,channels : list) :
            new_pathway = Pathway(
                name=name,
                guild_id=interaction.guild_id,
                exp_cooldown=10
                )
            channel_instances = [Channel(id=int(channel),guild_id=interaction.guild_id) for channel in channels]
            session = connection.Session()
            try : 
                for inst in channel_instances : 
                    merge_instance = session.merge(inst)
                    new_pathway.channels.append(merge_instance)
                    
                session.add(new_pathway) 
                session.commit()
            except Exception as e : await interaction.response.send_message(embeds=[error_embed(e)])
            finally : session.close()

            embed = discord.Embed(title="Se ha creado una ruta")
            embed.add_field(name="Ruta",value=name)
            embed.add_field(name="exp_cooldown",value=new_pathway.exp_cooldown)
            embed.add_field(name="Canales",value=",".join([interaction.guild.get_channel(int(channel)).name for channel in channels]))
            
            await interaction.response.send_message(embeds=[embed])
             
        view = Select_pathway_channel_view(submit_callback=handleSubmit) 
        await ctx.respond(f"Seleccione los canales que debe monitorizar esta ruta",view=view,ephemeral=True)
        
    @commands.slash_command()
    @default_permissions(manage_roles=True)
    async def pathway_delete (self,ctx : discord.ApplicationContext,name : str) : 
        session = connection.Session()
        try :  
            pathway_to_delete = session.execute(
                select(Pathway)
                .where(Pathway.name == name)
                ).scalars().first()
            
            if pathway_to_delete is None : 
                await ctx.respond(embed = error_embed(f"No existe una ruta con el nombre {name}"))
                return
            
            async def handleSubmit (interaction : discord.Interaction,input_name : str) :  
                if input_name.strip() == name.strip() : 
                    session.delete(pathway_to_delete)
                    session.commit()
                    await interaction.response.send_message(embed=discord.Embed(title=f"Ruta {name} eliminada con éxito"))
                    return
                await interaction.response.send_message(embed =discord.Embed(title="palabra clave incorrecta"))
                
            
            modal = Delete_name_confirmation(name=name,submit_callback=handleSubmit)
            await ctx.send_modal(modal)
        except Exception as e : await ctx.respond(embed=error_embed(e))
        finally : session.close()
        
    @commands.slash_command()
    @default_permissions(manage_roles=True)
    async def pathway_add_role (self,ctx : discord.ApplicationContext,pathway_name : str,level : int) : 
        session = connection.Session()
        try :  
            finded_pathway = await self.handle_missing_pathway(session,ctx,pathway_name)
            if finded_pathway is None : return 
        
            async def view_submit (interaction:discord.Interaction,selected_role_id : str) :
                try :
                    pathway = session.execute(
                        select(Pathway).where(Pathway.id == finded_pathway.id)
                    ).scalar_one_or_none()
                    discord_id : int = int(selected_role_id)
                    new_role = Role(
                        discord_id =discord_id,
                        pathway_id=pathway.id,
                        level=int(level)
                        )
                    session.add(new_role)
                    session.commit() 
                    embed = discord.Embed(
                        title="Rol asociado",
                        description=f"el rol {get(interaction.guild.roles,id=discord_id).name} se ha asociado correctamente a la ruta {pathway_name}, el rol sera asignado automáticamente a todos los usuarios que alcancen el nivel {level} en esta ruta."
                        )
                    await interaction.response.send_message(embed=embed)
                except IntegrityError : await interaction.respond(embed=error_embed(f"Este rol ya pertenece a la ruta {pathway_name}, o ya existe un rol asignado al nivel {level} de esta ruta"))
         
            view = V_select_role(on_submit=view_submit) 
            await ctx.respond("Seleccione un rol",view=view,ephemeral=True)  
        except Exception as e : await ctx.respond(embed=error_embed(e))
        finally : session.close()
        
    @default_permissions(manage_roles=True)
    @commands.slash_command()
    async def pathway_remove_role (self,ctx : discord.ApplicationContext,pathway_name : str) : 
        #buscar en la bd los roles asignados al pathway
        session = connection.Session()
        guild_id = ctx.guild_id
        try :
            pathway_roles = session.execute(
                select(Role.id,Pathway.id,Role.discord_id)
                .where(
                    Pathway.guild_id == guild_id,
                    Pathway.name == pathway_name
                    )
                .join(Pathway.roles)
            ).all()
            if pathway_roles is None : return
            print(f"roles:{pathway_roles}")
            pathway_id = pathway_roles[0][1]
            res_roles = [(
                get(ctx.guild.roles,id=pathway_role[2]).name,
                str(pathway_role[0])
                ) for pathway_role in pathway_roles]
            async def on_submit (interaction:discord.Interaction,roles : List[int]) : 
                try:
                    print("submited roles",roles)
                    session.execute(
                        delete(Role)
                        .where(Role.id.in_(roles))
                    )
                
                    embed = discord.Embed(
                        title="Roles desasociados exitosamente",
                        description=f"Se han desasociados los siguientes roles de la ruta {pathway_name}"
                        )
                    
                    for role in res_roles : 
                        print(f"{role[0]} is in {roles} ???")
                        if int(role[1]) in roles :  
                            embed.add_field(name=role[0],value=f"id: {role[1]}",inline=False)
                    
                    session.commit()    
                    await interaction.response.send_message(embed=embed)
                except Exception as e : 
                    await interaction.respond(embed=error_embed(e))
                                
            view = V_select_pathway_roles(
                roles=res_roles,
                on_submit=on_submit
            )
            print("finded:",res_roles) 
            # await ctx.respond("respuesta de prueba")
            await ctx.respond(view=view)
        except Exception as e : 
            print("_"*65,"ERROR:",e)
            await ctx.respond(embed = error_embed(e))
            
    async def handle_missing_pathway (self,session : Session,ctx:discord.ApplicationContext,pathway_name : str) : 
        finded_pathway = session.execute(
                select(Pathway)
                .where(Pathway.guild_id == ctx.guild_id,Pathway.name == pathway_name.strip())
                ).scalar_one_or_none()
        if finded_pathway is None : 
            await ctx.respond(embed=error_embed("No existe una ruta con este nombre"))
            return None
        
        return finded_pathway

        
    