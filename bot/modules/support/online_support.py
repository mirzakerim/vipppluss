from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from utils.database import create_connection, execute_query, fetch_query
from bot.modules.common.menu import show_user_menu

# Define states for the conversation
DEPARTMENT, QUESTION = range(2)

async def start_support(update: Update, context: CallbackContext) -> int:
    departments = ['Sales', 'Technical', 'Billing', 'Other']
    reply_markup = ReplyKeyboardMarkup([[d] for d in departments] + [['Cancel']], one_time_keyboard=True)
    await update.message.reply_text(
        'Please choose the department you want to contact:',
        reply_markup=reply_markup,
    )
    return DEPARTMENT

async def choose_department(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Cancel':
        await show_user_menu(update, context)
        return ConversationHandler.END

    context.user_data['department'] = update.message.text
    await update.message.reply_text(
        'Please enter your question:',
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
        await update.message.reply_text("Failed to connect to the database.")
        return ConversationHandler.END

    query = "SELECT id FROM users WHERE telegram_id = %s"
    user_data = (telegram_id,)
    user_id = None

    try:
        result = fetch_query(connection, query, user_data)
        if result:
            user_id = result[0][0]
        else:
            await update.message.reply_text("User not found in the database.")
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        return ConversationHandler.END

    # Save support request to the database
    query = """
    INSERT INTO support_requests (user_id, department, question, status)
    VALUES (%s, %s, %s, 'unanswered')
    """
    data = (user_id, department, question)

    try:
        execute_query(connection, query, data)
        await update.message.reply_text('Thank you! Your question has been submitted to the support team.')
        
        # ارسال سوال به ادمین‌های مشخص شده
        await send_question_to_admins(context, department, question, user_id)

        # بازگشت به منوی اصلی و پایان مکالمه
        await show_user_menu(update, context)
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        return ConversationHandler.END
    finally:
        connection.close()

async def cancel(update: Update, context: CallbackContext) -> int:
    await show_user_menu(update, context)
    return ConversationHandler.END

async def send_question_to_admins(context: CallbackContext, department: str, question: str, user_id: int):
    admin_ids = {
        'Sales': [6445960938, 6623572261],  # ID‌های ادمین‌های دپارتمان Sales
        'Technical': [6445960938, 6623572261],  # ID‌های ادمین‌های دپارتمان Technical
        'Billing': [6445960938, 6623572261],  # ID‌های ادمین‌های دپارتمان Billing
        'Other': [6445960938, 6623572261]  # ID‌های ادمین‌های دپارتمان Other
    }
    message = f"New support request from user {user_id}:\nDepartment: {department}\nQuestion: {question}"
    for admin_id in admin_ids.get(department, []):
        await context.bot.send_message(chat_id=admin_id, text=message)
