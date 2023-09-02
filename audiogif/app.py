from dotenv import load_dotenv
import logging
from os import environ as env
from service.telegram_service import TelegramService
from service.video_service import VideoService
from database.repository import Repository
from telegram.ext import Updater, MessageHandler, Filters, InlineQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()

BOT_ID= env['BOT_ID']
TOKEN = env['TOKEN']
MANAGEMENT_CHANNEL_ID = env['MANAGEMENT_CHANNEL_ID']
DB_PATH = env['DB_PATH']
SEARCH_PATH = env['SEARCH_PATH']

def main():

    telegram_service = provision_services()

    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(InlineQueryHandler(telegram_service.handle_bot_mention))
    dispatcher.add_handler(MessageHandler(Filters.video, telegram_service.handle_video_upload))
    dispatcher.add_handler(MessageHandler(Filters.reply, telegram_service.handle_message_reply))

    updater.start_polling()

def provision_services() -> TelegramService:
    #TODO: use DI
    repository = Repository(DB_PATH)
    service = VideoService(repository)

    return TelegramService(BOT_ID, TOKEN, MANAGEMENT_CHANNEL_ID, service)

if __name__ == '__main__':
    main()