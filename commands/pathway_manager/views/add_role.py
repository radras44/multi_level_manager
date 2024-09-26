import discord
class Pathway_add_role_view (discord.ui.View) : 
    def __init__ (self,submit_callback,pathways : dict) : 
        super().__init__()
        self.selected_role = None
        self.selected_pathway = None
        self.minimum_level = None
        self.pathways = pathways
        self.submit_callback = submit_callback
        
        role_select= discord.ui.Select(
            placeholder="rol",
            select_type=discord.ComponentType.channel_select,
            channel_types=[discord.ChannelType.text] 
        )
        role_select.callback = self.role_select_callback
        self.add_item(role_select) 
        
        pathway_options = [discord.SelectOption(label=pathway) for pathway in self.pathways]
        pathway_select = discord.ui.Select(
            placeholder="Ruta",
            options=pathway_options,
        )
        pathway_select.callback = self.pathway_select_callback
        self.add_item(pathway_select)
        
        submit_button = discord.ui.Button(
            label="Enviar",
            custom_id="submit_button"
        )
        submit_button.callback = self.submit
        self.add_item(submit_button)
        
    async def role_select_callback (self,interaction : discord.Interaction) :
        role_id = interaction.data["values"][0]
        self.selected_role = role_id
        await interaction.response.defer()
        
    async def pathway_select_callback(self,interaction : discord.Interaction):
        pathway = interaction.data["values"][0]
        self.selected_pathway = pathway
        await interaction.response.defer()
        
    async def submit (self,interaction : discord.Interaction) :
        modal = Level_modal(modal_callback=self.modal_callback)
        await interaction.response.send_modal(modal)
    
    async def modal_callback (self,interaction : discord.Interaction,level : str) :
                await self.submit_callback()
        

class Level_modal (discord.ui.Modal) :
    def __init__ (self,modal_callback,*args,**kwargs) : 
        super().__init__(title="Nivel requerido",*args,**kwargs)
        self.modal_callback = modal_callback
        self.add_item(discord.ui.InputText(
            label="escriba un numero"
        ))
        
    async def callback (self,interaction : discord.Interaction) :
        level = self.children[0].value
        if level.isdigit() : 
            await self.modal_callback(interaction=interaction,level=level)
        else : 
            await interaction.response.send_message(f"valor para nivel requerido incorrecto, debe escribir un numero")
        

        
    