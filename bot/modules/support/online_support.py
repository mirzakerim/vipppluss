import requests
from telegram import Update, ForceReply, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.database import create_connection, execute_query, fetch_query
from bot.modules.common.menu import show_user_menu
from config import ADMIN_BOT_TOKEN
from utils.logger import get_logger

logger = get_logger(__name__)

# Define states for the conversation
DEPARTMENT, QUESTION = range(2)

async def start_support(update: Update, context: CallbackContext) -> int:
    departments = ['فروش', 'فنی', 'مالی', 'سایر']
    reply_markup = ReplyKeyboardMarkup([['فروش', 'فنی'], ['مالی', 'سایر'], ['لغو']], one_time_keyboard=True)
    await update.message.reply_text(
        'لطفاً بخشی که می‌خواهید با آن تماس بگیرید را انتخاب کنید:',
        reply_markup=reply_markup,
    )
    return DEPARTMENT

async def choose_department(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'لغو':
        await show_user_menu(update, context)
        return ConversationHandler.END

    context.user_data['department'] = update.message.text
    await update.message.reply_text(
        'لطفاً سوال خود را وارد کنید:',
        reply_markup=ForceReply(selective=True),
    )
    return QUESTION

async def ask_question(update: Update, context: CallbackContext) -> int:
    context.user_data['question'] = update.message.text
    telegram_id = update.message.from_user.id
    department = context.user_data['department']
    question = context.user_data['question']

    # Get user_id from the users table
    connection = create_connection()
    if connection is None:
        await update.message.reply_text("اتصال به پایگاه داده ناموفق بود.")
        return ConversationHandler.END

    query = "SELECT id FROM users WHERE telegram_id = %s"
    user_data = (telegram_id,)
    user_id = None

    try:
        result = fetch_query(connection, query, user_data)
        if result:
            user_id = result[0][0]
        else:
            await update.message.reply_text("کاربر در پایگاه داده یافت نشد.")
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"خطایی رخ داد: {e}")
        return ConversationHandler.END

    # Save support request to the database
    query = """
    INSERT INTO support_requests (user_id, telegram_id, department, question, status)
    VALUES (%s, %s, %s, %s, 'unanswered')
    """
    data = (user_id, telegram_id, department, question)

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        ticket_id = cursor.lastrowid  # دریافت ID تیکت جدید
        cursor.close()

        logger.info(f"Ticket ID {ticket_id} saved to database for user {telegram_id}")

        await update.message.reply_text('متشکریم! سوال شما به تیم پشتیبانی ارسال شد.')

        # ارسال سوال به ادمین‌های مشخص شده
        success = await send_question_to_admins(context, ticket_id, department, question, user_id)
        if not success:
            await update.message.reply_text("خطایی در ارسال پیام به ادمین‌ها رخ داد.")

        # بازگشت به منوی اصلی و پایان مکالمه
        await show_user_menu(update, context)
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error saving ticket to database: {e}")
        await update.message.reply_text(f"خطایی رخ داد: {e}")
        return ConversationHandler.END
    finally:
        connection.close()

async def cancel(update: Update, context: CallbackContext) -> int:
    await show_user_menu(update, context)
    return ConversationHandler.END

async def send_question_to_admins(context: CallbackContext, ticket_id: int, department: str, question: str, user_id: int) -> bool:
    admin_ids = {
        'فروش': [6623572261, 987654321],  # ID‌های ادمین‌های دپارتمان فروش
        'فنی': [6623572261, 987654321],  # ID‌های ادمین‌های دپارتمان فنی
        'مالی': [6623572261, 987654321],  # ID‌های ادمین‌های دپارتمان مالی
        'سایر': [6623572261, 987654321]  # ID‌های ادمین‌های دپارتمان سایر
    }
    message = f"درخواست پشتیبانی جدید از کاربر {user_id}:\nبخش: {department}\nسوال: {question}\nتیکت ID: {ticket_id}"

    success = True
    for admin_id in admin_ids.get(department, []):
        url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': admin_id,
            'text': message,
            'reply_markup': InlineKeyboardMarkup(
                [[InlineKeyboardButton("پردازش سوال", callback_data=f'process_question_{ticket_id}')]]
            ).to_dict()  # تبدیل InlineKeyboardMarkup به دیکشنری
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send message to admin {admin_id}: {response.text}")
            success = False
        else:
            logger.info(f"Sent message to admin {admin_id} with ticket ID {ticket_id}")
    return success

def main():
    from telegram.ext import Updater
    updater = Updater(ADMIN_BOT_TOKEN)

    dispatcher = updater.dispatcher

    support_handler = ConversationHandler(
        entry_points=[CommandHandler('support', start_support)],
        states={
            DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_department)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(support_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
