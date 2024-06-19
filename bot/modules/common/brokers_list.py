from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

async def get_brokers_list(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    brokers_message = (
        "✅دوستاني كه در بروكر\n"
        "لايت فاينسس هستيد 👇🏻👇🏻👇🏻\n\n"
        "كد 298723518 براي انتقال\n\n"
        "—————————————————————————————--\n\n"
        "✅دوستاني كه در بروكر\n"
        "اوپو  هستيد 👇🏻👇🏻👇🏻\n\n"
        "كد  127979 براي انتقال\n\n"
        "——————————————————————————————-\n\n"
        "✅دوستاني كه در بروكر\n"
        "الپاري هستيد 👇🏻👇🏻👇🏻\n\n"
        "كد 170005754 براي انتقال\n\n"
        "——————————————————————————————-\n\n"
        "✅دوستاني كه در  بروکر\n"
        "ای مارکت هستيد 👇🏻👇🏻👇🏻\n\n"
        "كد DJ6OK براي انتقال\n\n"
        "——————————————————————————————-\n\n"
        "✅دوستاني كه در بروکر \n"
        "آرون گروپس  هستيد 👇🏻👇🏻👇🏻\n\n"
        "كد 122122  براي انتقال\n\n"
        "لینک ثبت نام :\n"
        "https://client.arongroups.co/links/go/1040"
    )

    keyboard = [
        ["بازگشت به منو قبلی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(chat_id=chat_id, text=brokers_message, reply_markup=reply_markup)

async def back_to_vip_menu(update: Update, context: CallbackContext) -> None:
    from bot.modules.user.vip_membership import start_vip_purchase
    await start_vip_purchase(update, context)
