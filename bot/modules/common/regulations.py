from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

async def regulations(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    message1 = (
        "❌❌❌ استفاده از ربات و خدمات نیک گلد به منزله  مطالعه و تایید همه قوانین است "
        "پس لطفا همه قوانین و مقررات را بطور کامل مطالعه فرمایید❌❌❌"
    )
    await context.bot.send_message(chat_id=chat_id, text=message1)

    message2 = (
        "١)مطالعه و تسلط كامل بر پست هاي آموزشي كه مربوط به استفاده از سيگنال هاي فاركس مي باشد. ( در كانال اموزشي نيك گلد)\n"
        "٢)رعايت كامل نكات مربوط به مديريت سرمايه و ريسك ، روانشناسي معامله و عدم اصرار به معامله در نقاط هيجاني و حساس بازار (بسيار مهم)\n"
        "٣)سود و زيان هر دو عضو جدايي ناپذيري از بازارهاي مالي است . با رعايت كردن حد ضرر و نيز پذيرفتن هر دو سمت اين بازار ، در بازار ماندگار خواهيد شد ولي چنانچه بر احساسات خود نسبت به سود و زيان ،كنترلي نداشته باشيد بهتر است مدت بيشتري تجربه كسب كنيد و سپس مجدد وارد معاملات واقعي شويد پس با علم به پذيرش ماهيت بازارهاي مالي وارد معامله شويد.\n"
        "٤)عدم استفاده از سيگنال هاي شخصي ،عجولانه و هيجاني\n"
        "٥)استفاده از تمامي سيگنال هاي اعلام شده در روز (عدم انتخاب سيگنال براي معامله) به جز #پريسك كه فقط براي اعضاء با ريسك بالا مورد استفاده است.\n"
        "٦)در صورت دارا بودن بالانس زير 100 دلار حتما به حساب سنتي متصل شويد.\n"
        "٧)به ازاي هر 100 تنها 0.01 لات وارد معامله شويد و در اهداف اول سيو سود كنيد.\n"
        "٨)قرار دادن حد ضرر در تمامي اوردرها الزامي است.\n\n"
        "''با تشكر تيم تحليلي نيك گلد''"
    )

    keyboard = [
        ["بازگشت به منو اصلی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await context.bot.send_message(chat_id=chat_id, text=message2, reply_markup=reply_markup)

async def back_to_menu(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("/menu")

