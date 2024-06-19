from telegram import Update
from telegram.ext import CallbackContext

def check_level(update: Update, context: CallbackContext):
    update.message.reply_text("Here is your current level.")
