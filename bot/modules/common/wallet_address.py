from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

async def get_wallet_address(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    wallet_message_1 = "آدرس ولت تتر روی شبکه trc20"
    wallet_message_2 = "TSHysDLkKBdNP1enVPAxJNi7MYEsqcFHi7"

    keyboard = [
        ["بازگشت به منو قبلی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(chat_id=chat_id, text=wallet_message_1)
    await context.bot.send_message(chat_id=chat_id, text=wallet_message_2, reply_markup=reply_markup)

async def back_to_vip_menu(update: Update, context: CallbackContext) -> None:
    from bot.modules.user.vip_membership import start_vip_purchase
    await start_vip_purchase(update, context)
