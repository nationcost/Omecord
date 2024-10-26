import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=',',
            intents=discord.Intents(
                guilds=True, 
                members=True,
                messages=True, 
                message_content=True),
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="/calluser"))
        
    async def setup_hook(self):
        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✔︎ Loaded {filename}")
                except Exception as e:
                    print(f"✗ Failed to load {filename}: {e}")

    async def on_ready(self):
        # Set status to /calluser
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.streaming,
                name="/calluser"))
        print(f'Omecord is ready! Chat with random strangers online: {self.user}')



if __name__ == "__main__":
    bot = Bot()
    bot.run(DISCORD_TOKEN)