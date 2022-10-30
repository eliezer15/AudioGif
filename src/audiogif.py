from dotenv import load_dotenv
import logging
from os import environ as env
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters, InlineQueryHandler
from telegram import Update, InlineQueryResultArticle, InlineQueryResultCachedVideo

from video_repository import VideoRepository

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()

BOT_ID= env['BOT_ID']
TOKEN = env['TOKEN']
MANAGEMENT_CHANNEL_ID = env['MANAGEMENT_CHANNEL_ID']

video_repo = VideoRepository(env['DB_FILE'])

def main():
    
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    #dispatcher.add_handler(InlineQueryHandler(on_mention))
    dispatcher.add_handler(MessageHandler(Filters.video, on_video_upload))
    dispatcher.add_handler(MessageHandler(Filters.reply, on_message_reply))

    updater.start_polling()

def on_video_upload(update: Update, context: CallbackContext):
    print(update)
    if not is_management_channel(update):
        return

    if update.message.via_bot and update.message.via_bot.is_bot:
        return
   
    caption = '' if update.message.caption is None else update.message.caption.lower() 
    output_message = video_repo.save_video(caption, update.message.video, update.message.from_user)

    update.message.reply_text(output_message)

def on_message_reply(update: Update, context: CallbackContext):
    if update.message.reply_to_message.video is None:
        print('Ignoring, not video')
        return

    reply_text = update.message.text.strip().lower()
    if reply_text not in ['favorite', 'favorito', 'f', '❤️', '⭐']:
        return

    output_message = video_repo.favorite(update.message.reply_to_message.video, update.message.from_user)
    update.message.reply_text(output_message)

def on_mention(update: Update, context: CallbackContext):
        query = update.inline_query.query
        user_id = update.inline_query.from_user.id
        captions = video_repo.search_video_captions(query, str(user_id))

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
    return str(update.message.chat_id) == MANAGEMENT_CHANNEL_ID

if __name__ == '__main__':
    main()