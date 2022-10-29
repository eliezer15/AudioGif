from dotenv import load_dotenv
import logging
from os import environ as env
from typing import Dict, List
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters, InlineQueryHandler
from telegram import Update, InlineQueryResultArticle, InlineQueryResultCachedVideo

load_dotenv()

VIDEOS_FILE = env.get('VIDEOS_FILE')
BOT_ID= env.get('BOT_ID')
TOKEN = env.get('TOKEN')
MANAGEMENT_CHANNEL_ID = env.get('MANAGEMENT_CHANNEL_ID')

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
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
    output_message = ''

    caption = '' if not  update.message.caption else update.message.caption.lower() 

    if caption == '':
        output_message = 'El video no incluye ningun caption, no sera guardado.'

    elif len(caption) > 32:
        output_message = 'El caption tiene mas de 32 caracteres. Sube el video con un caption mas corto.'
    
    else:
        with open(VIDEOS_FILE, mode='r+') as data_file:
            captions_to_video_ids = build_dict_from_file(data_file)

            if caption in captions_to_video_ids:
                output_message = f'Otro video ya usa el caption "{caption}." Sube el video con un caption diferente.'
            else:
                data_file.write(f'\n{caption}={video_id}')
                output_message = 'Video guardado exitosamente.'
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=output_message)

def on_mention(update: Update, context: CallbackContext):
    with open(VIDEOS_FILE) as data_file:
        captions_to_video_ids = build_dict_from_file(data_file)
        query = update.inline_query.query
        commands = filter_commands(query, captions_to_video_ids.keys())

        results = []
        for command in commands:
            results.append(
                build_inline_query(command, captions_to_video_ids)
            )

        context.bot.answer_inline_query(update.inline_query.id, results)

def build_dict_from_file(data_file) -> Dict:
    dict = {}
    for line in data_file:
        values = line.split('=')
        if (len(values) < 2):
            continue
        dict[values[0]] = values[1].strip()
    
    return dict

def build_inline_query(command: str, captions_to_video_ids: Dict) -> InlineQueryResultArticle:
    print(captions_to_video_ids)
    return InlineQueryResultCachedVideo(
        id=command,
        title=command,
        video_file_id=captions_to_video_ids[command]
    )

def filter_commands(query: str, video_captions: List) -> List:
    if len(query) > 2:
        return list(filter(lambda prompt: query in prompt, video_captions))
    else:
        return video_captions

def is_management_channel(update: Update) -> bool:
    print(update.message.chat_id)
    return str(update.message.chat_id) == MANAGEMENT_CHANNEL_ID

if __name__ == '__main__':
    main()