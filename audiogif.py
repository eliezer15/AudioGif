from dotenv import load_dotenv
import logging
from os import environ as env
from typing import Dict
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters, InlineQueryHandler
from telegram import Update, InlineQueryResultArticle, InlineQueryResultCachedVideo

from video_repository import VideoRepository

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()

#TODO: Separate constants from env variables

BOT_ID= env.get('BOT_ID')
TOKEN = env.get('TOKEN')
MANAGEMENT_CHANNEL_ID = env.get('MANAGEMENT_CHANNEL_ID')

video_repo = VideoRepository(env.get('VIDEOS_FILE'))

def main():
    
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(InlineQueryHandler(on_mention))
    dispatcher.add_handler(MessageHandler(Filters.video, on_video_upload))

    updater.start_polling()

def on_video_upload(update: Update, context: CallbackContext):
    print(update)

    if not is_management_channel(update):
        return

    if update.message.via_bot and update.message.via_bot.is_bot:
        return
   
    video_id = update.message.video.file_id
    caption = '' if not  update.message.caption else update.message.caption.lower() 

    output_message = video_repo.save_video(caption, video_id)

    context.bot.send_message(chat_id=update.effective_chat.id, text=output_message)

def on_mention(update: Update, context: CallbackContext):
        query = update.inline_query.query
        captions = video_repo.search_video_captions(query)

        results = []
        for caption in captions:
            results.append(
                build_inline_query(caption, video_repo.get_video_id(caption))
            )

        context.bot.answer_inline_query(update.inline_query.id, results)

def build_inline_query(video_caption: str, video_id: str) -> InlineQueryResultArticle:
    return InlineQueryResultCachedVideo(
        id=video_caption,
        title=video_caption,
        video_file_id=video_id
    )

def is_management_channel(update: Update) -> bool:
    print(update.message.chat_id)
    return str(update.message.chat_id) == MANAGEMENT_CHANNEL_ID

if __name__ == '__main__':
    main()