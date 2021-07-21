from __future__ import annotations
from abc import ABC, abstractmethod
from os import environ
from dotenv import load_dotenv
from logging import basicConfig, getLogger, INFO
from configparser import ConfigParser
from requests import get
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from telegram import Update
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

load_dotenv()
TOKEN = environ.get('TOKEN')
RSS_BRIDGE = environ.get('RSS_BRIDGE')

basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=INFO
)

logger = getLogger(__name__)


def is_url_valid(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def sanitize_markdown_string(text: str) -> str:
    return text.replace('-', '\-').replace('.', '\.').replace('!', '\!')


def build_rss_bridge_feed(bridge: str, arguments: dict) -> str:
    required_query = dict(
        action='display', media_type='all', format='Atom')
    required_query['bridge'] = bridge
    query = required_query | arguments
    setup = (
        'https',  # scheme
        f"{RSS_BRIDGE}",  # netloc
        '/',  # path
        '',  # params
        f"{urlencode(query)}",  # query
        ''  # fragment
    )
    return urlunparse(setup)


class FeedSource(ABC):
    @abstractmethod
    def __init__(self, url: str):
        pass

    @staticmethod
    @abstractmethod
    def validate_url(url: str, update: Update) -> bool:
        if is_url_valid(url):
            if YouTube.validate_url(url=url):
                return "YouTube"
            if Instagram.validate_url(url=url):
                return "Instagram"
            else:
                update.message.reply_text(
                    'Looks like I do not support such link')
                logger.warn(f'Could not parse link {url}')
        else:
            update.message.reply_text('Looks like this is not a URL')
            logger.warn(f'Not a URL {url}')

    @abstractmethod
    def generate_rss(self, url: str) -> str:
        pass


class Instagram(FeedSource):

    def __init__(self, url: str):
        if "explore/tags" in url:
            self.id_type = "Hashtag"
            self.short_type = "h"
        else:
            self.id_type = "Username"
            self.short_type = "u"

    @staticmethod
    def validate_url(url: str):
        if "instagram.com" not in url:
            return False
        return True

    def generate_rss(self, url: str) -> str:
        content_id = urlparse(url).path.split("/")[-2]
        logger.info(f"Instagram {self.id_type} '{content_id}'")
        arguments = {
            'context': self.id_type,
            self.short_type: content_id
        }
        feed_url = build_rss_bridge_feed(
            bridge="Instagram", arguments=arguments)
        return f"Enjoy your Instagran {self.id_type} feed\n{feed_url}"


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
        return f"Enjoy your YouTube {self.id_type} RSS:\nhttps://www.youtube.com/feeds/videos.xml?{self.id_type}_id={content_id}"


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(sanitize_markdown_string(
        """I can generate RSS feeds with the help of [rss-bridge](https://github.com/RSS-Bridge/rss-bridge)
Now I'm able to generate feeds for
- YouTube: channels and playlists
- Instagram: profiles and hashtags
*I am not a feed reader!* I only generate RSS feed that you can use with another Telegram bot or your reader of choice
Thanks for using. You can see bot source code on [github](https://github.com/wunderwaffla/rss-my-ass)"""), parse_mode='MarkdownV2')


def create_rss(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    feed_type = FeedSource.validate_url(url=url, update=update)
    if feed_type:
        if feed_type == "Instagram":
            feed = Instagram(url=url)
        elif feed_type == "YouTube":
            feed = YouTube(url=url)
        link = feed.generate_rss(url=url)
        update.message.reply_text(link)


def main() -> None:

    if TOKEN is None:
        logger.error(
            'Please specify TOKEN environment variable with Telegram bot token')
        exit(1)
    if RSS_BRIDGE is None:
        logger.error(
            'Please specify RSS_BRIDGE environment variable with rss-bridge hostname')
        exit(1)

    updater = Updater(environ.get('TOKEN'))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("start", help_command))

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, create_rss))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
