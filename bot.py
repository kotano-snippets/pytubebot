"""This bot can download videos from YouTube
using links inside user messages.
"""

import os
import re
import json
from pathlib import Path

import requests
import telebot
import pytube


def load(fname) -> dict:
    with open(fname, 'r') as f:
        contents = json.load(f)
    return contents


config = load('config.json')
replies = load('replies.json')

bot = telebot.TeleBot(config["token"])


KB_MAIN = telebot.types.ReplyKeyboardMarkup().add('/help')


def download_video(url) -> str:
    """Download video from youtube and return path to file."""
    video = pytube.YouTube(url)
    # Download highest resolution video and save it inside /videos folder.
    vfile = video.streams.get_highest_resolution().download('./videos')
    # Return path to downloaded file.
    return vfile


def get_video_from_tg(message):
    """Helper method. Get video contained in telegram message.

    Args:
        message (object): Telebot message.

    Returns:
        Object: reqeusts.Response object.
    """
    telegram_file_path = bot.get_file(message.video.file_id).file_path
    file = requests.get(
        'https://api.telegram.org/file/bot{0}/{1}'.format(
            config['test_token'], telegram_file_path))
    return file


@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    """Send help message to user.

    Args:
        message (object): Telebot message.

    Returns:
        object: Telebot message.
    """
    return bot.reply_to(
        message,
        replies["help"],
        reply_markup=KB_MAIN, disable_web_page_preview=True)


@bot.message_handler(commands=['meow'])
def meow(message):
    """Send short video to user."""
    video = download_video('https://youtu.be/tPEE9ZwTmy0')
    with open(str(Path(video)), 'rb') as f:
        res = bot.send_video(message.chat.id, f)
        return res


@bot.message_handler(content_types=['text'])
def handle_youtube_link(message) -> list:
    """Send videofiles from youtube.
    Looks for youtube video links inside message and returns videofile.

    Args:
        message (object): Telebot message object.

    Returns:
        list: List of sent messages
    """
    cid = message.chat.id
    # Define regular expression.
    # Looks for all sentences containing `youtu` word.
    # `\S` means 'everything except whitespace`.
    regex = r"\S*youtu\S*"
    links = re.findall(regex, message.text)
    res = []
    # Get video from every link.
    for match in links:
        try:
            video = download_video(match)
        # If it is not a proper link, continue.
        except pytube.exceptions.RegexMatchError:
            continue
        # Normalize downloaded video path.
        vnormpath = str(Path(video))
        with open(str(vnormpath), 'rb') as f:
            msg = bot.send_video(
                cid, f, reply_to_message_id=message.message_id)
        res.append(msg)
        # Remove downloaded video from local storage.
        os.remove(vnormpath)
    return res


def main():
    bot.polling()


if __name__ == "__main__":
    main()
