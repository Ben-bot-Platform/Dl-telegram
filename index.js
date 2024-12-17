const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const BOT_TOKEN = '7615192443:AAEGBZsdzqef7b8XNSfyCyZkigM9R27U6j0';
const bot = new TelegramBot(BOT_TOKEN, { polling: true });

const YOUTUBE_API = 'https://nayan-video-downloader.vercel.app/ytdown?url=';
const FACEBOOK_API = 'https://nayan-video-downloader.vercel.app/alldown?url=';

const HELP_TEXT = `
Welcome to the BEN_BOT Downloader! 🎥

📌 Supported Platforms:
- YouTube
- Facebook
- Another soon

Send a link from one of these platforms to download the video in SD or HD quality.

🚀 Let's get started!

ᴘᴏᴡᴇʀᴇᴅ ʙʏ ɴᴏᴛʜɪɴɢ
`;

const user_data = {};

bot.onText(/\/(start|help|main)/, (msg) => {
    bot.sendMessage(msg.chat.id, HELP_TEXT);
});

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;

    if (text.startsWith('http')) {
        let apiUrl;
        let platform;

        if (text.includes('youtube.com') || text.includes('youtu.be')) {
            apiUrl = `${YOUTUBE_API}${text}`;
            platform = 'YouTube';
        } else if (text.includes('facebook.com')) {
            apiUrl = `${FACEBOOK_API}${text}`;
            platform = 'Facebook';
        } else {
            bot.sendMessage(chatId, '❌ Unsupported platform. Please provide a valid YouTube or Facebook link.');
            return;
        }

        try {
            const response = await axios.get(apiUrl);
            const data = response.data;

            if (data.status) {
                const videoData = data.data;
                const title = videoData.title || platform;
                const thumbnail = videoData.thumb !== 'not available' ? videoData.thumb : null;
                const videoSD = videoData.low || videoData.video;
                const videoHD = videoData.high || videoData.video_hd;

                user_data[chatId] = {
                    sd: videoSD,
                    hd: videoHD,
                    title,
                };

                const caption = `🎬 *${title}*\n\n📥 Choose your preferred quality:\n\nᴘᴏᴡᴇʀᴇᴅ ʙʏ ɴᴏᴛʜɪɴɢ`;

                const options = {
                    reply_markup: {
                        inline_keyboard: [
                            [{ text: 'Download SD', callback_data: 'send_sd' }],
                            [{ text: 'Download HD', callback_data: 'send_hd' }],
                        ],
                    },
                    parse_mode: 'Markdown',
                };

                if (thumbnail) {
                    bot.sendPhoto(chatId, thumbnail, { caption, ...options });
                } else {
                    bot.sendMessage(chatId, caption, options);
                }
            } else {
                bot.sendMessage(chatId, '❌ Video not found. Please provide a valid link.');
            }
        } catch (error) {
            bot.sendMessage(chatId, '❌ Error connecting to the server. Please try again.');
            console.error(error);
        }
    }
});

bot.on('callback_query', async (callbackQuery) => {
    const chatId = callbackQuery.message.chat.id;
    const data = callbackQuery.data;
    const videoDetails = user_data[chatId];

    if (!videoDetails) {
        bot.answerCallbackQuery(callbackQuery.id, '❌ No video data found. Please try again.');
        return;
    }

    const quality = data === 'send_sd' ? 'SD' : 'HD';
    const videoUrl = data === 'send_sd' ? videoDetails.sd : videoDetails.hd;
    const title = videoDetails.title;

    bot.answerCallbackQuery(callbackQuery.id, `📥 Sending ${quality} video...`);

    try {
        await bot.sendVideo(chatId, videoUrl, {
            caption: `🎬 *${title}*\n📥 Quality: ${quality}\n\nᴘᴏᴡᴇʀᴇᴅ ʙʏ ɴᴏᴛʜɪɴɢ`,
            parse_mode: 'Markdown',
        });
    } catch (error) {
        bot.sendMessage(chatId, '❌ Failed to send the video. Please try again.');
        console.error(error);
    }
});

console.log('%cBot is active', 'color: green; background-color: white; font-size: 20px;');