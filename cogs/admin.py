import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1299777797266341949  # The channel where notifications will be sent

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Get the log channel
        log_channel = self.bot.get_channel(self.log_channel_id)
        if not log_channel:
            return  # If channel not found, silently return
        
        # Try to get audit logs to find who added the bot
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                if entry.target.id == self.bot.user.id:
                    inviter = entry.user
                    break
            else:
                inviter = None
        except discord.Forbidden:
            inviter = None

        # Create embed
        embed = discord.Embed(
            title="New Server Join!",
            color=discord.Color.green()
        )

        # Add server information
        embed.add_field(
            name="Server Info",
            value=f"**{inviter.name if inviter else 'Unknown'}** added {self.bot.user.name} in "
                  f"**{guild.name}** with {guild.member_count} Members.",
            inline=False
        )

        # Add additional server details
        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="Server Owner", value=str(guild.owner), inline=True)
        
        # Set server icon as thumbnail if available
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Add timestamp
        embed.timestamp = discord.utils.utcnow()

        # Send the embed
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # Get the log channel
        log_channel = self.bot.get_channel(self.log_channel_id)
        if not log_channel:
            return

        # Create embed for server leave
        embed = discord.Embed(
            title="Bot Removed from Server",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Server Info",
            value=f"Bot was removed from **{guild.name}**",
            inline=False
        )

        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        
        # Add timestamp
        embed.timestamp = discord.utils.utcnow()

        # Send the embed
        await log_channel.send(embed=embed)

    @app_commands.command(name="invite", description="Get an invite link for a specific server (Admin only)")
    @app_commands.describe(server_id="The ID of the server to generate an invite for")
    async def invite(self, interaction: discord.Interaction, server_id: str):
        # Check if the user is authorized (you can modify this check as needed)
        authorized_users = [1061809969336852550]  # Add your user ID here
        if interaction.user.id not in authorized_users:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        try:
            # Convert server_id to int
            guild_id = int(server_id)
            
            # Get the guild
            guild = self.bot.get_guild(guild_id)
            if not guild:
                await interaction.response.send_message("I couldn't find that server or I'm not in it.", ephemeral=True)
                return

            # Try to create an invite
            try:
                # Get the first available channel that can create invites
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        invite = await channel.create_invite(
                            max_age=3600,  # 1 hour
                            max_uses=1,    # 1 use
                            unique=True
                        )
                        
                        # Create embed
                        embed = discord.Embed(
                            title="Server Invite Generated",
                            color=discord.Color.blue(),
                            description=f"Here's your invite link for **{guild.name}**"
                        )
                        embed.add_field(name="Invite Link", value=str(invite), inline=False)
                        embed.add_field(name="Duration", value="1 hour", inline=True)
                        embed.add_field(name="Max Uses", value="1 use", inline=True)
                        
                        if guild.icon:
                            embed.set_thumbnail(url=guild.icon.url)
                            
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                
                # If no suitable channel was found
                await interaction.response.send_message("Couldn't find a suitable channel to create an invite.", ephemeral=True)
                
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to create invites in that server.", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("Please provide a valid server ID.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))