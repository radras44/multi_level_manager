import discord

class V_select_pathway_roles (discord.ui.View) :
    def __init__(self,roles : tuple,on_submit):
        super().__init__()
        self.selected_roles = []
        self.on_submit = on_submit
        role_select = discord.ui.Select(
            max_values=len(roles),
            options=[
                discord.SelectOption(label=role[0],value=role[1],description=str(role[1]))
                for role in roles
            ]
        )
        role_select.callback = self.role_select_callback
        self.add_item(role_select)
        
        submit_button = discord.ui.Button(
            label="Eliminar"
        )
        submit_button.callback = self.submit_button_callback
        self.add_item(submit_button)
        
        
    async def role_select_callback (self,interaction : discord.Interaction) :
        selected_role_ids = interaction.data["values"]
        self.selected_roles = selected_role_ids
        await interaction.response.defer()
        
    async def submit_button_callback (self,interaction : discord.Interaction) :
        await self.on_submit(interaction,[int(role_id) for role_id in self.selected_roles])