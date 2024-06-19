import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    CallbackContext, ConversationHandler, MessageHandler, filters, CommandHandler
)
from utils.database import create_connection
from telegram.error import BadRequest, TimedOut
import pymysql  # وارد کردن کتابخانه pymysql

# Logging Setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Conversation States
SELECT_SUBSCRIPTION, RECEIPT, TRANSACTION_ADDRESS = range(3)

# Constants for messages
ASK_SUBSCRIPTION_MSG = "لطفاً نوع اشتراک مورد نظر خود را انتخاب کنید:\n1. VIP\n2. VIP+"
ASK_RECEIPT_MSG = "لطفاً رسید خود را ارسال کنید."
ASK_TRANSACTION_ADDRESS_MSG = "لطفاً آدرس تراکنش را ارسال کنید:"
RECEIPT_ERROR_MSG = "خطا در دریافت فایل. لطفاً مجدداً تلاش کنید."
INVALID_FILE_TYPE_MSG = "لطفاً یک عکس یا سند معتبر ارسال کنید."
DB_ERROR_MSG = "خطا در ذخیره اطلاعات. لطفاً مجدداً تلاش کنید."
THANK_YOU_MSG = "با تشکر از شما. بعد از بررسی تراکنش و درخواست توسط ادمین، لینک یک بار مصرف کانال برای شما ارسال خواهد شد."
CANCEL_MSG = "فرایند ارسال رسید لغو شد."

# Keyboard for subscription selection
subscription_keyboard = [
    ["VIP", "VIP+"]
]
reply_markup = ReplyKeyboardMarkup(subscription_keyboard, resize_keyboard=True, one_time_keyboard=True)

async def start_receipt_process(update: Update, context: CallbackContext) -> int:
    """Starts the receipt submission process."""
    user = update.message.from_user
    logger.info(f"Starting receipt process for user: {user.username}")

    await update.message.reply_text(ASK_SUBSCRIPTION_MSG, reply_markup=reply_markup)
    return SELECT_SUBSCRIPTION

async def select_subscription(update: Update, context: CallbackContext) -> int:
    """Handles the subscription selection and moves to the next step."""
    user = update.message.from_user
    subscription = update.message.text

    if subscription not in ["VIP", "VIP+"]:
        await update.message.reply_text("لطفاً یک گزینه معتبر انتخاب کنید.")
        return SELECT_SUBSCRIPTION

    # Map user-friendly names to database ENUM values
    subscription_enum = 'vip' if subscription == "VIP" else 'vip_plus'

    context.user_data['subscription'] = subscription_enum
    await update.message.reply_text(ASK_RECEIPT_MSG)
    return RECEIPT

async def handle_file(update: Update, context: CallbackContext) -> str:
    """Handles the receipt (photo or document) and returns the file path."""
    user = update.message.from_user

    if update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_ext = '.jpg'  # Assuming JPEG for photos
        file_id = update.message.photo[-1].file_id
        file_unique_id = update.message.photo[-1].file_unique_id
    elif update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        file_ext = os.path.splitext(update.message.document.file_name)[1]
        file_id = update.message.document.file_id
        file_unique_id = update.message.document.file_unique_id
    else:
        raise ValueError("Invalid file type")

    # Sanitize file name
    safe_file_name = f"{user.id}_{file_unique_id}{file_ext}"
    file_path = os.path.join('receipts', safe_file_name)

    # Ensure the receipts directory exists
    os.makedirs('receipts', exist_ok=True)

    # Download the file correctly
    await file.download_to_drive(file_path)  

    logger.info(f"Received file from {user.username}: {file_path}")

    # Save file info in context.user_data
    context.user_data['file_path'] = file_path
    context.user_data['file_id'] = file_id
    context.user_data['file_unique_id'] = file_unique_id

    return file_path

async def receive_receipt(update: Update, context: CallbackContext) -> int:
    """Handles the receipt and prompts for the transaction address."""
    try:
        await handle_file(update, context)
    except (BadRequest, TimedOut) as e:
        logger.error(f"Error downloading file: {e}")
        await update.message.reply_text(RECEIPT_ERROR_MSG)
        return await back_to_menu(update, context)
    except ValueError:
        await update.message.reply_text(INVALID_FILE_TYPE_MSG)
        return await back_to_menu(update, context)

    await update.message.reply_text(ASK_TRANSACTION_ADDRESS_MSG)
    return TRANSACTION_ADDRESS

async def receive_transaction_address(update: Update, context: CallbackContext) -> int:
    """Handles the transaction address input and saves to the database."""
    user = update.message.from_user
    transaction_address = update.message.text

    # Database Update (with enhanced error handling)
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO vip_requests (user_id, username, subscription, file_id, file_unique_id, 
                                          file_path, transaction_address, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user.id, user.username, context.user_data['subscription'], context.user_data['file_id'], context.user_data['file_unique_id'], context.user_data['file_path'], transaction_address, 'pending')
            )
        connection.commit()
    except pymysql.MySQLError as e:
        logger.error(f"Error saving data to database: {e}")
        await update.message.reply_text(DB_ERROR_MSG)
        return await back_to_menu(update, context)
    finally:
        connection.close()

    await update.message.reply_text(THANK_YOU_MSG)
    return await back_to_menu(update, context)

async def back_to_menu(update: Update, context: CallbackContext) -> int:
    """Returns the user to the main menu."""
    from bot.modules.common.menu import show_user_menu
    await show_user_menu(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels the receipt submission process."""
    await update.message.reply_text(CANCEL_MSG)
    return await back_to_menu(update, context)

def get_receipt_conv_handler() -> ConversationHandler:
    """Creates and returns the ConversationHandler for the receipt submission process."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^ارسال رسید و ثبت نام$'), start_receipt_process)],
        states={
            SELECT_SUBSCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_subscription)],
            RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, receive_receipt)],
            TRANSACTION_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_transaction_address)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
