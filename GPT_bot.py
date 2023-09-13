import discord
import openai
import re
from youtube_transcript_api import YouTubeTranscriptApi

openai.api_key = "*****************"  # I should be using environment variables

async def handle_message(message, messages=None):
    if message.author.bot:
        return

    author_display_name = message.author.display_name  # Extract the display name

    system_prompt = (
        f"You are a Discord bot called AiLa, sometimes users may refer to you as <@1095267084897886229> which stands for Artificial Intelligent Language Bot. Your job is to help people improve their English Language skills, but you can have friendly chats with people as well."
        f"The person you are talking to is called {author_display_name}."
        "Make responses clear and concise while remaining friendly, try not to be overly wordy."
        "When asked to define words, or explain grammar, you answer with Simple English explanations."
        "You also are able to summarise text - Tell the user that is done by @ messaging you and providing a Youtube link as their message."
    )

    if not isinstance(messages, list):  # Proper indentation
        messages = []

    youtube_url_regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|v\/|u\/\w\/|embed\/)|youtu\.be\/)([\w\-]{11})"
    matches = re.findall(youtube_url_regex, message.content)

    if matches:
        video_id = matches[0]
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([entry['text'] for entry in transcript_data])
            response_content = f"Provide a simple English summary of this text, which is a video transcript in a few paragraphs, format your writing correctly make it easy to read - The author of the video is not the user: {transcript}."
            messages.append({"role": "assistant", "content": response_content})
        except Exception as e:
            await message.channel.send(f"Sorry {author_display_name}, I couldn't fetch the transcript for that video. Error: {e}")
            return

    current_chat = [{"role": "system", "content": system_prompt}] + messages

    print(f"Sending this chat to OpenAI: {current_chat}")

    try:
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo-16k",
          messages=current_chat,
          temperature=1,
          max_tokens=2500,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        message_content = response.choices[0].message['content'].strip()
        print(f"Received response from OpenAI: {message_content}")
    except Exception as e:
        message_content = f"There's an error here: {str(e)}"
        print(f"Error occurred when calling OpenAI: {str(e)}")

    char_limit = 2000
    split_responses = [message_content[i:i+char_limit] for i in range(0, len(message_content), char_limit)]

    for resp in split_responses:
        await message.channel.send(resp)