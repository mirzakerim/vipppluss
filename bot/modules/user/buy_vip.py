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
        "ضمن خوش آمدگويي به شما كاربر عزيز\n"
        "تيم نيك گلد بعد از گذشت 2 سال براي خدمات بي نظير خود در بازارهاي مالي و به ويژه تحليل نماد طلا در فاركس ، افزايش هزينه دارد.\n\n"
        "***براي دريافت اشتراك كانال سيگنال دهي انس طلا (كانال 24 ساعته و با سابقه ي وين_ريت100 در 33 ماه )\n"
        "(نكته : وين ريت 100 در كارنامه ي ماست اين ماركت در هر لحظه امكان ضرر دهي دارد و اين به معناي تداوم ان نيست)\n\n"
        "1. اشتراك يك ماهه 70$( USDT)\n"
        "(با ورود كد بروكر 10$ تخفيف بگيريد)\n\n"
        "2. اشتراك دو ماهه 130$ ( USDT)\n"
        "(با ورود كد بروكر 15$ تخفيف بگيريد)\n\n"
        "3. اشتراك سه ماهه 180$ ( USDT)\n"
        "(با ورود كد بروكر 20$ تخفيف بگيريد)\n\n"
        "به دليل اينكه براي تمديد اعضاء نياز به تاييد توسط استاد هست از اشتراك بيشتر از 3 ماه معذوريم\n"
        "و به دليل ارائه ي تحليل هاي بلند مدتي از اشتراك كمتر از 1 ماه هم معذوريم 🙏🏻\n\n"
        "با توجه به بازدهي بسيار عالي كانال نيك گلد اين مبالغ حتي با داشتن 100 دلار سرمايه هم ، نا چيز است 😍"
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
