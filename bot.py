import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Telegram bot token
BOT_TOKEN = "7615192443:AAEGBZsdzqef7b8XNSfyCyZkigM9R27U6j0"
bot = telebot.TeleBot(BOT_TOKEN)

# API URLs
YOUTUBE_API = "https://nayan-video-downloader.vercel.app/ytdown?url="
FACEBOOK_API = "https://nayan-video-downloader.vercel.app/alldown?url="

HELP_TEXT = """
Welcome to the BEN_BOT Downloader! 🎥

📌 Supported Platforms:
- YouTube
- Facebook
- Another soon

Send a link from one of these platforms to download the video in SD or HD quality.

🚀 Let's get started!

ᴘᴏᴡᴇʀᴇᴅ ʙʏ ɴᴏᴛʜɪɴɢ
"""

# Temporary user data
user_data = {}

@bot.message_handler(commands=['start', 'help', 'main'])
def send_welcome(message):
    bot.send_message(message.chat.id, HELP_TEXT)

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def process_video_link(message):
    video_url = message.text

    # Determine platform
    if "youtube.com" in video_url or "youtu.be" in video_url:
        api_url = YOUTUBE_API + video_url
        platform = "YouTube"
    elif "facebook.com" in video_url:
        api_url = FACEBOOK_API + video_url
        platform = "Facebook"
    else:
        bot.send_message(message.chat.id, "❌ Unsupported platform. Please provide a valid YouTube or Facebook link.")
        return

    # Fetch video data from API
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if data["status"]:
            video_data = data["data"]
            title = video_data.get("title", platform)
            thumbnail = video_data.get("thumb", "")
            video_sd = video_data.get("low" if platform == "Facebook" else "video", "")
            video_hd = video_data.get("high" if platform == "Facebook" else "video_hd", "")

            # Save video details for the user
            user_data[message.chat.id] = {
                "sd": video_sd,
                "hd": video_hd,
                "title": title
            }

            # Thumbnail for Facebook
            if thumbnail == "not available":
                thumbnail = None

            # Send response with buttons
            caption = f"🎬 *{title}*\n\n📥 Choose your preferred quality:\n\nᴘᴏᴡᴇʀᴇᴅ ʙʏ ɴᴏᴛʜɪɴɢ"
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("Download SD", callback_data="send_sd"),
                InlineKeyboardButton("Download HD", callback_data="send_hd")
            )

            # Send thumbnail if available
            if thumbnail:
                bot.send_photo(message.chat.id, thumbnail, caption=caption, reply_markup=markup, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, caption, reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Video not found. Please provide a valid link.")
    else:
        bot.send_message(message.chat.id, "❌ Error connecting to the server. Please try again.")

@bot.callback_query_handler(func=lambda call: call.data in ["send_sd", "send_hd"])
def send_video(call):
    video_details = user_data.get(call.message.chat.id)
    if not video_details:
        bot.answer_callback_query(call.id, "❌ No video data found. Please try again.")
        return

    # Determine quality
    video_url = video_details["sd"] if call.data == "send_sd" else video_details["hd"]
    title = video_details["title"]

    # Notify user
    bot.answer_callback_query(call.id, f"📥 Sending {call.data.split('_')[1].upper()} video...")

    try:
        # Send video
        bot.send_video(call.message.chat.id, video=video_url, caption=f"🎬 *{title}*\n📥 Quality: {call.data.split('_')[1].upper()}\n\nᴘᴏᴡᴇʀᴇᴅ ʙʏ ɴᴏᴛʜɪɴɢ", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ Failed to send the video. Please try again.")
        print(f"Error: {e}")
print("Bot is active")
bot.infinity_polling()