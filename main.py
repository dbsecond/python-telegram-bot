import logging
import os
import shutil

from model import StyleTransferModel
from io import BytesIO
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


model = StyleTransferModel()
first_image_file = {}

@run_async
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! This is style transfer bot. Please upload content image')

@run_async
def text_handler(update, context):
    """Echo the user message."""
    update.message.reply_text('Please use /start command for start')

@run_async
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

@run_async
def image_handler(update, context):
    chat_id = update.message.chat_id
    id = str(update.message.chat.id)
    if not os.path.exists(id):
        os.makedirs(id)
    image_id = update.message.photo[0].file_id
    file = context.bot.getFile(image_id)
    if os.path.isfile('{}/content.jpg'.format(id)):
        file.download('{}/style.jpg'.format(id))
        update.message.reply_text('Processing!')
        output = model.process_image('{}/content.jpg'.format(id), '{}/style.jpg'.format(id))
        output_stream = BytesIO()
        output.save(output_stream, format='PNG')
        output_stream.seek(0)
        context.bot.send_photo(chat_id, photo=output_stream)
        shutil.rmtree(id)
    else:
        file.download('{}/content.jpg'.format(id))
        update.message.reply_text('Ok, then upload style image')


def main():

    updater = Updater("", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text_handler))

    dp.add_handler(MessageHandler(Filters.photo, image_handler))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

