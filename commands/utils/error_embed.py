import discord

def error_embed (e) :
    return discord.Embed(title="Error").add_field(name="Descripcion",value=str(e))