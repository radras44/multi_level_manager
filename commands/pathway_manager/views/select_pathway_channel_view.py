import discord
class Select_pathway_channel_view (discord.ui.View) :
    def __init__ (self,submit_callback) :
        super().__init__()
        self.submit_callback = submit_callback

        channel_select = discord.ui.Select(
            select_type=discord.ComponentType.channel_select,
            channel_types=[discord.ChannelType.text],
            max_values=10
        )
            
        channel_select.callback = self.channel_select_callback
        self.add_item(channel_select)
        
        submit_button = discord.ui.Button(
            label="Guardar"
        )
        submit_button.callback = self.submit
        self.add_item(submit_button)
        
    async def channel_select_callback (self,interaction : discord.Interaction) : 
        self.channels = interaction.data["values"]
        await interaction.response.defer()
        
    async def submit (self,interaction : discord.Interaction) :
        print("canales capturados",self.channels)
        await self.submit_callback(interaction,self.channels)
        
    
    