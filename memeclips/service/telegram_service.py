import json
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

        if str(message.chat_id) == self.management_channel_id:
            return
            
        if message.via_bot and message.via_bot.is_bot:
            return
    
        caption = '' if message.caption is None else message.caption.lower()

        video = Video.from_telegram_video(message.video)
        user = User.from_telegram_user(message.from_user)

        output_message = self.video_service.save_video(caption, video, user)

        message.reply_text(output_message)

    def handle_message_reply(self, update: Update, context: CallbackContext):
        message = update.message

        if message.reply_to_message.video is None:
            return

        reply_text = message.text.strip().lower()
        if reply_text not in ['favorite', 'favorito', 'f', '❤️', '⭐']:
            return

        video = Video.from_telegram_video(message.reply_to_message.video)
        user = User.from_telegram_user(message.from_user)

        output_message = self
        message.reply_text(output_message)

    def handle_bot_mention(self, update: Update, context: CallbackContext):
        query = update.inline_query.query
        get_default_videos_for_user = len(query) == 0
        user = User.from_telegram_user(update.inline_query.from_user)

        videos = self.video_service.search_videos(query, user, get_default_videos_for_user)

        results = []
        for video in videos:
            results.append(self.__build_inline_query(video))

        context.bot.answer_inline_query(
            update.inline_query.id, 
            results,
            is_personal=get_default_videos_for_user)

    def __build_inline_query(self, video: Video) -> InlineQueryResultArticle:
        return InlineQueryResultCachedVideo(
            id=video.title,
            title=video.title,
            video_file_id=video.playable_video_id
        )