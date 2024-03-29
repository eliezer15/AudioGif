import json
import random
import string
from typing import List
from service.domain_models import Video, User
from service.video_service import VideoService
from telegram.ext import CallbackContext
from telegram import Message, InlineQueryResultArticle, InlineQueryResultCachedVideo, Update

class TelegramService:
    def __init__(self, bot_id: str, token: str, management_channel_id: str, video_service: VideoService):
        self.bot_id = bot_id
        self.token = token
        self.management_channel_id = management_channel_id
        self.video_service = video_service

    def handle_video_upload(self, update: Update, context: CallbackContext):
        message = update.message
        
        if str(message.chat_id) != self.management_channel_id:
            return
            
        if message.via_bot and message.via_bot.is_bot:
            return
    
        caption = '' if message.caption is None else message.caption.lower()

        video = Video.from_telegram_video(message.video, caption)
        user = User.from_telegram_user(message.from_user)

        output_message = self.video_service.save_video(caption, video, user)

        message.reply_text(output_message)

    def handle_message_reply(self, update: Update, context: CallbackContext):
        message = update.message

        if message.reply_to_message.video is None:
            return

        reply_text = message.text.strip().lower()
        if reply_text == 'f':
            self.__handle_favorite_command(message)
        
        elif reply_text == 'd':
            self.__handle_delete_command(message)
        
        elif reply_text == 'uf':
            self.__handle_delete_favorite_command(message)

        elif reply_text.startswith('e'):
            self.__handle_edit_title(message, reply_text)
        else:
            return

    def handle_bot_mention(self, update: Update, context: CallbackContext):
        query = update.inline_query.query.strip().lower()

        user = User.from_telegram_user(update.inline_query.from_user)

        videos = self.video_service.search_videos(query, user)

        results = []
        count = 1
        for video in videos:
            count += 1
            results.append(self.__build_inline_query(video))

        update.inline_query.answer(
            results=results,
            is_personal=True, # only cache per user
            auto_pagination=True
        )
    
    def __handle_favorite_command(self, message: Message):
        video = Video.from_telegram_video(message.reply_to_message.video)
        user = User.from_telegram_user(message.from_user)

        output_message = self.video_service.save_favorite(video, user)
        message.reply_text(output_message)

    def __handle_delete_command(self, message: Message):
        video = Video.from_telegram_video(message.reply_to_message.video)
        output_message = self.video_service.delete_video(video)
        message.reply_text(output_message)

    def __handle_delete_favorite_command(self, message: Message):
        video = Video.from_telegram_video(message.reply_to_message.video)
        user = User.from_telegram_user(message.from_user)
        output_message = self.video_service.delete_favorite(video, user)
        message.reply_text(output_message)
    
    def __handle_edit_title(self, message: Message, reply_text: str):
        video = Video.from_telegram_video(message.reply_to_message.video)
        new_title = reply_text.split(':')[1].strip()
        output_message = self.video_service.update_video_title(video, new_title)
        message.reply_text(output_message)

    def __build_inline_query(self, video: Video) -> InlineQueryResultArticle:
        return InlineQueryResultCachedVideo(
            id=TelegramService.__build_random_id(),
            title=video.title,
            video_file_id=video.playable_video_id
        )
    
    def __build_random_id():
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(10))
