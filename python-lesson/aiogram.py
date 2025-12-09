import os
import re
from aiogram import Bot, Dispatcher, executor, types
from yt_dlp import YoutubeDL

TOKEN = "8023296312:AAFZvasvkaPKwvmfkPHXf5Q7AmoDaJLSvNg"
DOWNLOAD_DIR = "downloads"
LIMIT = 50 * 1024 * 1024
bot = Bot(TOKEN)
dp = Dispatcher(bot)

class QuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def quiet_hook(d): pass

def clean_filename(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9а-яА-ЯёЁ\-_(). ]', '', name)

def try_download(url: str, fmt: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'logger': QuietLogger(),
        'progress_hooks': [quiet_hook],
        'noplaylist': True,
        'format': fmt,
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s'
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            clean = clean_filename(filename)
            if clean != filename:
                os.rename(filename, clean)
                filename = clean
            return filename, info
    except Exception:
        return None, None

@dp.message_handler()
async def download(msg: types.Message):
    url = msg.text.strip()
    if not url.startswith(("http", "https")):
        return await msg.answer("To‘g‘ri link yuboring.")
    await msg.answer("⏳ Video yuklanmoqda...")
    formats = [
        "best[height<=720][ext=mp4]",
        "best[height<=480][ext=mp4]",
        "best[height<=360][ext=mp4]",
        "best[height<=240][ext=mp4]",
        "worst[ext=mp4]"
    ]
    for fmt in formats:
        filepath, info = try_download(url, fmt)
        if filepath and os.path.exists(filepath):
            size = os.path.getsize(filepath)
            if size <= LIMIT:
                title = info.get("title", "Video")
                with open(filepath, "rb") as f:
                    await msg.answer_video(f, caption=f"{title}")
                os.remove(filepath)
                return
            else:
                os.remove(filepath)
    await msg.answer("Eng past sifat ham 50MB dan katta")

if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    executor.start_polling(dp, skip_updates=True)
