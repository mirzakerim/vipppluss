from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from bot.modules.common.send_receipt import start_receipt_process
from bot.modules.common.brokers_list import get_brokers_list
from bot.modules.common.wallet_address import get_wallet_address
from utils.logger import get_logger

logger = get_logger(__name__)

async def start(update: Update, context: CallbackContext) -> int:
    logger.info("Starting registration process for user: %s", update.message.from_user.username)
    # سایر کدها
async def start_vip_purchase(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    welcome_message = (
        "شرايط عضويت در كانال تضميني به صورت زير است :\n\n"
        "1. اين كانال به صورت تضميني به شما سيگنال ارائه خواهد كرد و در صورتيكه برآيند يك ماهه سيگنال هاي ارائه شده در كانال منفي باشد مبلغ پرداخت شده ي شما عودت داده خواهد شد .\n\n"
        "2. به دليل اينكه هركسي كه عضو اين كانال باشد بايد حتما تريد داشته باشد و ما بايد از اين امر اطمينان حاصل كنيم\n"
        "حتما بايد كد همكاري بروكر توسط معامله گر وارد شود .\n\n"
        "3. تمامي دستورات بايد طبق كانال اجرا شود و تيم فقط برآيند اعلام شده در ورود و خروج هاي كانال را مورد بررسي قرار خواهد داد .\n\n"
        "4. تحليل و سيگنالدهي كاملا دقيق روي نماد تخصصي انس طلا .\n\n"
        "5. در اين كانال حدضرر ها كوتاه و هدف هاي كوتاه دارند و حدضرر اتوماتيك دارد و مناسب حساب هاي پراپ نيز هست .\n\n"
        "6. حق اشتراك ماهانه به دليل تضميني بودن برآيند مثبت اين كانال و مشخص بودن تمام ورود ها و خروج ها و كوتاه بودن حدضررها ، 200 USDT (تتر) خواهد بود."
    )

    await context.bot.send_message(chat_id=chat_id, text=welcome_message)

    regulations_message = (
        "❌❌❌ استفاده از ربات و خدمات نیک گلد به منزله  مطالعه و تایید همه قوانین است \n"
        "پس لطفا همه قوانین و مقررات را بطور کامل مطالعه فرمایید❌❌❌"
    )

    keyboard = [
        ["دریافت لیست بروکرها"],
        ["دریافت آدرس ولت"],
        ["ارسال رسید و ثبت نام"],
        ["بازگشت به منو اصلی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(chat_id=chat_id, text=regulations_message, reply_markup=reply_markup)

async def back_to_menu(update: Update, context: CallbackContext) -> None:
    from bot.modules.common.menu import show_user_menu
    await show_user_menu(update, context)
