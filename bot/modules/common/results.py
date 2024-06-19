from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

async def view_results(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    message = (
        "برای نمایش نتایج اعضای خانواده نیک گلد کافیست وارد لینک زیر بشید و و نتیجه حیرت انگیز بچه هارو تماشا کنید\n"
        "https://t.me/nikgold_Results"
    )

    keyboard = [
        ["بازگشت به منو اصلی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
