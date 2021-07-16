from __future__ import annotations
from abc import ABC, abstractmethod
from os import environ
from urllib.parse import urlparse, parse_qs
from telegram import Update
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from logging import basicConfig, getLogger, INFO
from requests import get


basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=INFO
)

logger = getLogger(__name__)


class FeedSource(ABC):
    @abstractmethod
    def __init__(self, url: str):
        pass

    @staticmethod
    @abstractmethod
    def validate_url(url: str, update: Update) -> bool:
        if YouTube.validate_url(url=url):
            return "YouTube"
        else:
            update.message.reply_text('Looks like I do not support such link')
            logger.warn(f'Could not parse link {url}')
        pass

    @abstractmethod
    def generate_rss(self, url: str) -> str:
        pass


class YouTube(FeedSource):

    def __init__(self, url: str):
        if "playlist" in url:
            self.id_type = "playlist"
        else:
            self.id_type = "channel"

    @staticmethod
    def validate_url(url: str):
        if "youtube" not in url and "youtu.be" not in url:
            return False
        return True

    def generate_rss(self, url: str) -> str:
        if self.id_type == "playlist":
            playlist_id = parse_qs(urlparse(url).query)['list'][0]
            print(playlist_id)
            logger.info(f"Youtube playlist id '{playlist_id}'")
            return self.create_rss_link(content_id=playlist_id)
        else:
            r = get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            for link in soup.find_all('meta'):
                if link.get('itemprop') == "channelId":
                    content_id = link.get('content')
                    logger.info(f"Youtube channel id '{content_id}'")
                    return self.create_rss_link(content_id=content_id)

    def create_rss_link(self, content_id: str) -> str:
        return f"Enjoy\nhttps://www.youtube.com/feeds/videos.xml?{self.id_type}_id={content_id}"


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Send me a link to YouTube channel and I\'ll generate RSS feed of the channel.\nI can also generate channel RSS from any video from that channel.\nAnd I can generate YouTube playlist RSS feed if you send me playlist URL')


def create_rss(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    feed_type = FeedSource.validate_url(url=url, update=update)
    if feed_type == "YouTube":
        feed = YouTube(url=url)
        link = feed.generate_rss(url=url)
        update.message.reply_text(link)


def main() -> None:
    TOKEN = environ.get('TOKEN')
    if environ.get('TOKEN') is None:
        logger.error(
            'Please specify TOKEN environment variable with Telegram bot token')
        exit(1)

    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, create_rss))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
