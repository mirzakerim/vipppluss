from telegram import Update
from telegram.ext import CallbackContext

async def faq(update: Update, context: CallbackContext):
    await update.message.reply_text("This is the FAQ section. Here you can find answers to common questions.")
