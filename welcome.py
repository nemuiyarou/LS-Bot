import discord
import openai
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up your OpenAI API key
openai.api_key = '***********************'

async def welcome_member(member):
    """
    Sends a welcome message to the member in the guild's system channel.
    """
    logging.info(f"Member {member.display_name} has joined.")
    
    channel = discord.utils.get(member.guild.text_channels, name="welcome👋")

    if channel is None:
        logging.error("Welcome channel not found.")
        return

    # Get the display name of the author
    author_display_name = member.display_name

    # Generate the welcome message using GPT-3
    prompt_message = f"Write a short simple english poem about {author_display_name} joining the discord server The Language Sauna, make it a bit silly and funny but easy to understand."
    response = get_gpt_response(prompt_message)
    
    final_welcome_message = f"Hi {member.mention}! I'm AiLa! I'm a ChatGPT bot designed to help you with your English Language learning. You can ask me general questions about anything 💪\n But I'm really good at explaining Grammar, defining Vocabulary and correcting writing!🤓\n You can also @ me and provide a Youtube Link, and I will summarise the video for you!\n Enough about me, here's a poem I wrote about you:{response}"

    await channel.send(final_welcome_message)

def get_gpt_response(prompt):
    """
    Fetch a response from GPT-3 based on the given prompt.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "system", "content": "You are a Discord bot called AiLa, which stands for Artifical Intelligen Language Bot. Your job is to help people improve their English Language skills, but you can have friendly chats with people as well."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=8960,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        logging.info("GPT-3 response fetched successfully.")
        return response.choices[0].message['content']

    except Exception as e:
        logging.error(f"GPT-3 API call failed. Error: {e}")
        return "I had trouble generating a response. Please try again later."