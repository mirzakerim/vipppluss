import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext, ConversationHandler, MessageHandler, filters, CommandHandler
)
from utils.database import create_connection
import pymysql

# Logging Setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Conversation States
PARTICIPATION, REASON, PROFIT_LOSS, AMOUNT, SCREENSHOT, THANK_YOU = range(6)

# Constants for messages
ASK_PARTICIPATION_MSG = "سلام! توی ترید امروز شرکت کردی؟"
ASK_REASON_MSG = "چرا شرکت نکردی؟"
ASK_PROFIT_LOSS_MSG = "سود کردی یا ضرر؟"
ASK_AMOUNT_MSG = "لطفا میزان {}تو برام بنویس:"
ASK_SCREENSHOT_MSG = "لطفا اسکرین شات هم بهم بده."
SORRY_MSG = "اوه! واقعا متاسفم که اینو میشنوم."
HOPE_MSG = "امیدوارم توی ترید بعدی بتونی جبران کنی."
THANK_YOU_MSG = "مرسی ازت!"
CANCEL_MSG = "فرایند ثبت سود و ضرر لغو شد."

# Keyboards
participation_keyboard = [["اره", "نه"]]
reason_keyboard = [["جاموندم", "آنلاین نبودم", "های ریسک بود", "سرمایه نداشتم"]]
profit_loss_keyboard = [["سود", "ضرر"]]

async def start_profit_loss(update: Update, context: CallbackContext) -> int:
    """Starts the profit/loss submission process."""
    user = update.message.from_user
    logger.info(f"Starting profit/loss process for user: {user.username}")

    reply_markup = ReplyKeyboardMarkup(participation_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(ASK_PARTICIPATION_MSG, reply_markup=reply_markup)
    return PARTICIPATION

async def receive_participation(update: Update, context: CallbackContext) -> int:
    """Handles the participation input and asks for the next step based on the response."""
    participation = update.message.text

    if participation == "نه":
        context.user_data['participation'] = participation
        reply_markup = ReplyKeyboardMarkup(reason_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(ASK_REASON_MSG, reply_markup=reply_markup)
        return REASON
    elif participation == "اره":
        context.user_data['participation'] = participation
        reply_markup = ReplyKeyboardMarkup(profit_loss_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(ASK_PROFIT_LOSS_MSG, reply_markup=reply_markup)
        return PROFIT_LOSS
    else:
        await update.message.reply_text("لطفا یک گزینه معتبر را انتخاب کنید.")
        return PARTICIPATION

async def receive_reason(update: Update, context: CallbackContext) -> int:
    """Handles the reason for not participating and ends the conversation."""
    reason = update.message.text
    context.user_data['reason'] = reason

    await update.message.reply_text(HOPE_MSG, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def receive_profit_loss(update: Update, context: CallbackContext) -> int:
    """Handles the profit/loss input and asks for the amount."""
    profit_loss = update.message.text

    if profit_loss == "ضرر":
        await update.message.reply_text(SORRY_MSG)
        await update.message.reply_text(ASK_AMOUNT_MSG.format("ضرر"))
        context.user_data['profit_loss'] = profit_loss
        return AMOUNT
    elif profit_loss == "سود":
        await update.message.reply_text("خیلی خوشحالم!")
        await update.message.reply_text(ASK_AMOUNT_MSG.format("سود"))
        context.user_data['profit_loss'] = profit_loss
        return AMOUNT
    else:
        await update.message.reply_text("لطفا یک گزینه معتبر را انتخاب کنید.")
        return PROFIT_LOSS

async def receive_amount(update: Update, context: CallbackContext) -> int:
    """Handles the amount input and asks for the screenshot if profit."""
    amount = update.message.text
    context.user_data['amount'] = amount

    if context.user_data['profit_loss'] == "سود":
        await update.message.reply_text(ASK_SCREENSHOT_MSG)
        return SCREENSHOT
    else:
        await update.message.reply_text(HOPE_MSG, reply_markup=ReplyKeyboardRemove())
        return await save_profit_loss(update, context)

async def receive_screenshot(update: Update, context: CallbackContext) -> int:
    """Handles the screenshot input and saves to the database."""
    screenshot = update.message.photo[-1].file_id if update.message.photo else None
    context.user_data['screenshot'] = screenshot

    await update.message.reply_text(THANK_YOU_MSG, reply_markup=ReplyKeyboardRemove())
    return await save_profit_loss(update, context)

async def save_profit_loss(update: Update, context: CallbackContext) -> int:
    """Saves the profit/loss data to the database."""
    user = update.message.from_user

    # Database Update (with enhanced error handling)
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO profit_loss (user_id, username, participation, reason, profit_loss, amount, screenshot) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user.id, user.username, context.user_data.get('participation'), context.user_data.get('reason'),
                 context.user_data.get('profit_loss'), context.user_data.get('amount'), context.user_data.get('screenshot'))
            )
        connection.commit()
    except pymysql.MySQLError as e:
        logger.error(f"Error saving data to database: {e}")
        await update.message.reply_text("خطا در ذخیره اطلاعات. لطفاً مجدداً تلاش کنید.")
        return ConversationHandler.END
    finally:
        connection.close()

    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels the profit/loss submission process."""
    await update.message.reply_text(CANCEL_MSG, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def get_profit_loss_conv_handler() -> ConversationHandler:
    """Creates and returns the ConversationHandler for the profit/loss submission process."""
    return ConversationHandler(
        entry_points=[CommandHandler('start_profit_loss', start_profit_loss)],
        states={
            PARTICIPATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_participation)],
            REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reason)],
            PROFIT_LOSS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_profit_loss)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)],
            SCREENSHOT: [MessageHandler(filters.PHOTO, receive_screenshot)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
