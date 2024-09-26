import discord
class Delete_name_confirmation (discord.ui.Modal) : 
    def __init__ (self,submit_callback,name,*args,**kwargs) : 
        super().__init__(*args,**kwargs,title=f"Escriba '{name}' para confirmar")
        self.submit_callback = submit_callback
        self.add_item(discord.ui.InputText(
            label="Palabra clave",
            style=discord.InputTextStyle.singleline
        ))
        
    async def callback (self,interaction : discord.Interaction) : 
        name = self.children[0].value
        await self.submit_callback(interaction,name)
        
        
    