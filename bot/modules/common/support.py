from telegram import Update
from telegram.ext import CallbackContext

async def support(update: Update, context: CallbackContext):
    await update.message.reply_text("This is the Support section. How can we help you today?")
