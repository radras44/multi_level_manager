import discord

class V_select_role (discord.ui.View) : 
    def __init__ (self,on_submit) : 
        super().__init__()
        self.on_submit = on_submit
        self.role_select = discord.ui.Select(
            placeholder="Role",
            select_type=discord.ComponentType.role_select
        )
        self.role_select.callback = self.callback
        self.add_item(self.role_select)
        
    async def callback (self,interaction : discord.Interaction) :
        role_id = interaction.data["values"][0]
        await self.on_submit(interaction,role_id)