from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.database import create_connection, execute_query, fetch_query
from bot.modules.common.menu import show_user_menu

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
    INSERT INTO support_requests (user_id, department, question, status)
    VALUES (%s, %s, %s, 'unanswered')
    """
    data = (user_id, department, question)

    try:
        execute_query(connection, query, data)
        await update.message.reply_text('متشکریم! سوال شما به تیم پشتیبانی ارسال شد.')
        
        # ارسال سوال به ادمین‌های مشخص شده
        await send_question_to_admins(context, department, question, user_id)

        # بازگشت به منوی اصلی و پایان مکالمه
        await show_user_menu(update, context)
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"خطایی رخ داد: {e}")
        return ConversationHandler.END
    finally:
        connection.close()

async def cancel(update: Update, context: CallbackContext) -> int:
    await show_user_menu(update, context)
    return ConversationHandler.END

async def send_question_to_admins(context: CallbackContext, department: str, question: str, user_id: int):
    admin_ids = {
        'فروش': [6445960938, 6623572261],  # ID‌های ادمین‌های دپارتمان فروش
        'فنی': [6445960938, 6623572261],  # ID‌های ادمین‌های دپارتمان فنی
        'مالی': [6445960938, 6623572261],  # ID‌های ادمین‌های دپارتمان مالی
        'سایر': [6445960938, 6623572261]  # ID‌های ادمین‌های دپارتمان سایر
    }
    message = f"درخواست پشتیبانی جدید از کاربر {user_id}:\nبخش: {department}\nسوال: {question}"
    for admin_id in admin_ids.get(department, []):
        await context.bot.send_message(chat_id=admin_id, text=message)

def main():
    from telegram.ext import Updater
    updater = Updater("YOUR_TOKEN")

    dispatcher = updater.dispatcher

    support_handler = ConversationHandler(
        entry_points=[CommandHandler('support', start_support)],
        states={
            DEPARTMENT: [MessageHandler(Filters.text & ~Filters.command, choose_department)],
            QUESTION: [MessageHandler(Filters.text & ~Filters.command, ask_question)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(support_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
