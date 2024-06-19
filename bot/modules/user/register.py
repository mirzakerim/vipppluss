from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from utils.database import create_connection, execute_query
from bot.modules.common.menu import show_user_menu

# Define states for the conversation
NAME, CONTACT_NUMBER, INVESTMENT_AMOUNT, HOW_MET, AGE, BROKER, MARKET_KNOWLEDGE = range(7)

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'Welcome! Please enter your name:',
        reply_markup=ForceReply(selective=True),
    )
    return NAME

async def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    contact_button = KeyboardButton(text="Share your contact number", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True)
    await update.message.reply_text(
        'Thank you! Please share your contact number:',
        reply_markup=reply_markup,
    )
    return CONTACT_NUMBER

async def contact_number(update: Update, context: CallbackContext) -> int:
    if update.message.contact:
        context.user_data['contact_number'] = update.message.contact.phone_number
    else:
        context.user_data['contact_number'] = update.message.text
    await update.message.reply_text(
        'Great! Please enter your investment amount:',
        reply_markup=ForceReply(selective=True),
    )
    return INVESTMENT_AMOUNT

async def investment_amount(update: Update, context: CallbackContext) -> int:
    context.user_data['investment_amount'] = update.message.text
    await update.message.reply_text(
        'Please let us know how you met us:',
        reply_markup=ForceReply(selective=True),
    )
    return HOW_MET

async def how_met(update: Update, context: CallbackContext) -> int:
    context.user_data['how_met'] = update.message.text
    await update.message.reply_text(
        'What is your age?',
        reply_markup=ForceReply(selective=True),
    )
    return AGE

async def age(update: Update, context: CallbackContext) -> int:
    context.user_data['age'] = update.message.text
    await update.message.reply_text(
        'Which broker do you use?',
        reply_markup=ForceReply(selective=True),
    )
    return BROKER

async def broker(update: Update, context: CallbackContext) -> int:
    context.user_data['broker'] = update.message.text
    await update.message.reply_text(
        'How much do you know about the market?',
        reply_markup=ForceReply(selective=True),
    )
    return MARKET_KNOWLEDGE

async def market_knowledge(update: Update, context: CallbackContext) -> int:
    context.user_data['market_knowledge'] = update.message.text

    # Save data to the database
    connection = create_connection()
    if connection is None:
        await update.message.reply_text("Failed to connect to the database.")
        return ConversationHandler.END

    user_data = (
        update.message.from_user.id,
        update.message.from_user.username,
        context.user_data['name'],
        context.user_data['contact_number'],
        context.user_data['investment_amount'],
        context.user_data['how_met'],
        context.user_data['age'],
        context.user_data['broker'],
        context.user_data['market_knowledge']
    )

    query = """
    INSERT INTO users (telegram_id, username, name, contact_number, investment_amount, how_met, age, broker, market_knowledge)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        execute_query(connection, query, user_data)
        await update.message.reply_text('Thank you for registering!')
    except Error as e:
        await update.message.reply_text(f"An error occurred: {e}")
    finally:
        connection.close()

    # نمایش منوی کاربران عادی پس از اتمام ثبت نام
    await show_user_menu(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Registration cancelled.')
    return ConversationHandler.END
