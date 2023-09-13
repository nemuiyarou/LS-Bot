import discord
from discord.ext import commands
import GPT_bot
import Flag_translate
from welcome import welcome_member

TOKEN = "************************"

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if the message is a reply
    if message.reference:
        # Fetch the message being replied to
        replied_to_message = await message.channel.fetch_message(message.reference.message_id)

        # If the replied-to message is from the bot
        if replied_to_message.author == bot.user:
            messages = [
                {"role": "assistant", "content": replied_to_message.content},
                {"role": "user", "content": message.content}
            ]

            await GPT_bot.handle_message(message, messages=messages)
            return  # Ensure we don't process further for this combined message

    # Call GPT_bot functionality when bot is mentioned
    if bot.user in message.mentions:
        messages = [{"role": "user", "content": message.content}]  # Create user message
        await GPT_bot.handle_message(message, messages=messages)  # Pass the user message to handle_message

    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    await Flag_translate.handle_reaction(payload, bot)
    
@bot.event
async def on_member_join(member):
    await welcome_member(member)  # Call the function to handle the member joining

bot.run(TOKEN)