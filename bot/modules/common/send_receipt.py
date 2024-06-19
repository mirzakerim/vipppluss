import os
import logging
from telegram import Update
from telegram.ext import (
    CallbackContext, ConversationHandler, MessageHandler, filters, CommandHandler
)
from utils.database import create_connection
from telegram.error import BadRequest, TimedOut

# Logging Setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Conversation States
RECEIPT, TRANSACTION_ADDRESS = range(2)


async def start_receipt_process(update: Update, context: CallbackContext) -> int:
    """Starts the receipt submission process."""
    user = update.message.from_user
    logger.info(f"Starting receipt process for user: {user.username}")

    await update.message.reply_text("لطفاً رسید خود را ارسال کنید.")
    return RECEIPT


async def receive_receipt(update: Update, context: CallbackContext) -> int:
    """Handles the receipt (photo or document) and transaction address."""
    user = update.message.from_user

    try:
        if update.message.photo:
            file = await context.bot.get_file(update.message.photo[-1].file_id)
            file_ext = '.jpg'  # Assuming JPEG for photos
        elif update.message.document:
            file = await context.bot.get_file(update.message.document.file_id)
            file_ext = os.path.splitext(update.message.document.file_name)[1]
        else:
            raise ValueError("Invalid file type")

        # Sanitize file name
        safe_file_name = f"{user.id}_{file.file_unique_id}{file_ext}"
        file_path = os.path.join('receipts', safe_file_name)

        # Ensure the receipts directory exists
        os.makedirs('receipts', exist_ok=True)

        # Download the file correctly
        await file.download_to_drive(file_path)  

        logger.info(f"Received file from {user.username}: {file_path}")

    except (BadRequest, TimedOut) as e:
        logger.error(f"Error downloading file: {e}")
        await update.message.reply_text("خطا در دریافت فایل. لطفاً مجدداً تلاش کنید.")
        return RECEIPT
    except ValueError:
        await update.message.reply_text("لطفاً یک عکس یا سند معتبر ارسال کنید.")
        return RECEIPT

    # Transaction Address Input
    await update.message.reply_text("لطفاً آدرس تراکنش را ارسال کنید:")
    context.user_data['file_path'] = file_path
    context.user_data['file_id'] = file.file_id
    context.user_data['file_unique_id'] = file.file_unique_id
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
                INSERT INTO vip_requests (user_id, username, file_id, file_unique_id, 
                                          file_path, transaction_address, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user.id, user.username, context.user_data['file_id'], context.user_data['file_unique_id'], context.user_data['file_path'], transaction_address, 'pending')
            )
        connection.commit()
    except Exception as e:  # Catch specific database errors if possible
        logger.error(f"Error saving data to database: {e}")
        await update.message.reply_text("خطا در ذخیره اطلاعات. لطفاً مجدداً تلاش کنید.")
        return TRANSACTION_ADDRESS
    finally:
        connection.close()

    await update.message.reply_text(
        "با تشکر از شما. بعد از بررسی تراکنش و درخواست توسط ادمین، لینک یک بار مصرف کانال برای شما ارسال خواهد شد."
    )

    # Return to Main Menu
    from bot.modules.user.menu import show_user_menu
    await show_user_menu(update, context)

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels the receipt submission process."""
    await update.message.reply_text("فرایند ارسال رسید لغو شد.")
    return ConversationHandler.END


def get_receipt_conv_handler() -> ConversationHandler:
    """Creates and returns the ConversationHandler for the receipt submission process."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^ارسال رسید و ثبت نام$'), start_receipt_process)],
        states={
            RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, receive_receipt)],
            TRANSACTION_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_transaction_address)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
