import discord
import openai
import logging
from langdetect import detect
import requests
import json

OPENAI_API_KEY = "***************"
openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

def detect_language(text):
    try:
        language = detect(text)
    except:
        language = "en"  # Default to English if detection fails
    return language

FLAG_LANGUAGE_MAP = {
    "🇬🇧": "en",
    "🇨🇦": "en",
    "🇦🇺": "en",
    "🇳🇿": "en",
    "🇺🇸": "en",
    "🇮🇪": "en",
    "🇮🇳": "hi",
    "🇵🇰": "ur",
    "🇧🇩": "bn",
    "🇮🇱": "he",
    "🇸🇦": "ar",
    "🇦🇪": "ar",
    "🇶🇦": "ar",
    "🇪🇬": "ar",
    "🇹🇷": "tr",
    "🇮🇷": "fa",
    "🇫🇷": "fr",
    "🇩🇪": "de",
    "🇮🇹": "it",
    "🇪🇸": "es",
    "🇲🇽": "es",
    "🇨🇴": "es",
    "🇦🇷": "es",
    "🇨🇱": "es",
    "🇧🇷": "pt",
    "🇵🇹": "pt",
    "🇷🇺": "ru",
    "🇯🇵": "ja",
    "🇨🇳": "zh",
    "🇰🇷": "ko",
    "🇻🇳": "vi",
    "🇮🇩": "id",
    "🇹🇭": "th",
    "🇸🇪": "sv",
    "🇳🇴": "no",
    "🇫🇮": "fi",
    "🇮🇸": "is",
    "🇳🇱": "nl",
    # Add more flags and their corresponding language codes as needed
}

def translate_text(text, source_language, target_language):
    if source_language == target_language:
        return text

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that translates text.",
                },
                {
                    "role": "user",
                    "content": f"Translate the following text from {source_language} to {target_language}: '{text}'",
                },
            ],
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))
        response_data = response.json()

        if response.status_code != 200:
            raise Exception(response_data.get("message", "Unknown error"))

        translated_text = response_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"Translation error: {e}")
        translated_text = "Translation error. Please try again later."

    return translated_text

async def handle_reaction(payload, bot_instance):
    logging.info("Reaction added")
    if payload.user_id == bot_instance.user.id:
        logging.info("Reaction by the bot, ignoring")
        return

    channel = bot_instance.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = bot_instance.get_user(payload.user_id)
    if str(payload.emoji) in FLAG_LANGUAGE_MAP:
        logging.info("Valid flag reaction detected")
        target_language = FLAG_LANGUAGE_MAP[str(payload.emoji)]

        source_language = detect_language(message.content)

        if source_language == target_language:
            logging.info("Source and target languages are the same, skipping translation")
            return

        logging.info(f"Translating from {source_language} to {target_language} for {user} via reaction")
        translated_text = translate_text(message.content, source_language, target_language)  # You can use bot_instance.loop.run_in_executor if needed
        logging.info(f"Translated text: {translated_text}")

        if translated_text.strip():
            await message.reply(f"{user.mention} requested a translation to {target_language}: {translated_text}", mention_author=True)
        else:
            logging.warning("Translated text is empty. Skipping sending the message.")
    else:
        logging.info("Reaction is not a valid flag, ignoring")