from twitchio.ext import commands
from dotenv import load_dotenv
import os
from googletrans import Translator

class Bot(commands.Bot):

    def __init__(self):
        """
        Initialise our Bot with our access token and prefix from a .env file, and a list of channels.
        
        """
        self.twitch_token = os.getenv('TWITCH_TOKEN')
        self.twitch_prefix = os.getenv('TWITCH_PREFIX')
        self.twitch_channels = os.getenv('TWITCH_CHANNELS').split(',')
        self.twitch_ignore = os.getenv('TWITCH_IGNORE').split(',')
        super().__init__(token=self.twitch_token, prefix=self.twitch_prefix, initial_channels=self.twitch_channels)

    async def event_ready(self):
        """"
        Reports what username and user id is logged in, and what channels it's connected to
        """
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

        for channel in self.twitch_channels:
            print(f'Connected to | {channel}')

    async def event_message(self, message):
        """
        Main method of reading through twitch chat
        """

        # Ignores messages by Twitch_Polyglot
        if message.echo:
            return
        # Ignores messages by nightbot or streamelements
        if message.author.name in self.twitch_ignore:
            return
        
        # Print the contents of our message to console and the detected langauge
        translator = Translator()
        translation = translator.translate(message.content)
        timestamp = message.timestamp.strftime("%H:%M:%S")
        print(f'{timestamp} - {message.channel.name}\{message.author.name} -  {message.content}, {translation.src}')

        # If Spanish is detected, sends the English translation to chat
        if translation.src == 'es':
            translation = translator.translate(message.content, dest='en')
            await message.channel.send(f'@{message.author.name}: {translation.text}')
        
        # Inline translate command, translating English to Spanish, with an error message if another langauge
        if "?translate" in message.content[:11].lower():
            if translation.src == 'en':
                translation = translator.translate(message.content[11:], dest='es')
                await message.channel.send(f'@{message.author.name}: {translation.text}')
            else:
                await message.channel.send(f'@{message.author.name}: I currently only handle manual English to Spanish translations')
            return

        await self.handle_commands(message)

    @commands.command()
    async def help(self, ctx: commands.Context):
        """Provides context of how the command works."""
        msg = f'Hello {ctx.author.name}! Just type in ?translate followed by your text to translate to Spanish'
        await ctx.send(msg)

# Checks if .env exists, and creates one if it doesn't
if os.path.isfile('.env') is False:
    with open('.env', 'w') as f:
        f.write('# .env\n')
        f.write('TWITCH_TOKEN=oauth:\n')
        f.write('TWITCH_PREFIX=?\n')
        f.write('TWITCH_CHANNELS=TWITCH\n')
        f.write('TWITCH_IGNORE=nightbot,streamelements')
    quit()
else:
    # Adds the variables from .env to enviromental variables
    load_dotenv()

bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.