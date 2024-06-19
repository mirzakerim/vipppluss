import sys
import os
import asyncio
import logging

from utils.logger import get_logger

# Logging Setup
logger = get_logger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

# Telegram Imports
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, CallbackContext
)

# Local Module Imports
from bot.modules.common import (
    regulations, results, menu, faq, brokers_list, wallet_address, send_receipt
)
from bot.modules.user import (
    register, buy_vipplus, buy_vip
)
from bot.modules.vip import (
    acc, profit_loss, renew_subscription
)
from bot.modules.support import online_support
from config import TOKEN, ADMINS
from utils.database import get_user_level

# --- Command and Message Handlers ---

def start(update: Update, context: CallbackContext) -> int:
    """Starts the registration process for new users."""
    logger.info("Starting registration process for user: %s", update.message.from_user.username)
    return register.start(update, context)


async def menu_command(update: Update, context: CallbackContext) -> int:
    """Displays the main menu to the user."""
    logger.info("User %s requested main menu", update.message.from_user.username)
    await menu.show_user_menu(update, context)
    return ConversationHandler.END


async def show_user_level(update: Update, context: CallbackContext):
    """Displays the user level to the user."""
    user = update.message.from_user
    user_level = get_user_level(user.id)

    if user_level:
        await update.message.reply_text(f"Your user level is: {user_level}")
    else:
        await update.message.reply_text("Unable to retrieve your user level.")


# --- Main Bot Setup ---
async def start_bot():
    """Initializes and starts the Telegram bot."""
    logger.info("Starting bot...")
    application = Application.builder().token(TOKEN).build()

    # Conversation Handler for Registration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            register.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register.name)],
            register.CONTACT_NUMBER: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), register.contact_number)],
            register.INVESTMENT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, register.investment_amount)],
            register.HOW_MET: [MessageHandler(filters.TEXT & ~filters.COMMAND, register.how_met)],
            register.AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register.age)],
            register.BROKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, register.broker)],
            register.MARKET_KNOWLEDGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register.market_knowledge)],
        },
        fallbacks=[CommandHandler('cancel', register.cancel), CommandHandler('menu', menu_command)],
    )

    # Conversation Handler for Support
    support_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Support$'), online_support.start_support)],
        states={
            online_support.DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, online_support.choose_department)],
            online_support.QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, online_support.ask_question)],
        },
        fallbacks=[CommandHandler('cancel', online_support.cancel), CommandHandler('menu', menu_command)],
    )

    
    # Add Conversation Handlers
    application.add_handler(conv_handler)
    application.add_handler(support_conv_handler)

    # Add Other Handlers
    application.add_handler(MessageHandler(filters.Regex(r'^FAQ$'), faq.faq))
    application.add_handler(MessageHandler(filters.Regex(r'^Buy VIP Membership$'), buy_vip.start_vip_purchase))
    application.add_handler(MessageHandler(filters.Regex(r'^Buy VIP\+ Membership$'), buy_vipplus.start_vip_purchase))
    application.add_handler(MessageHandler(filters.Regex(r'^View Results$'), results.view_results))
    application.add_handler(MessageHandler(filters.Regex(r'^Regulations$'), regulations.regulations))

    # VIP Membership Options
    application.add_handler(MessageHandler(filters.Regex('^دریافت لیست بروکرها$'), brokers_list.get_brokers_list))
    application.add_handler(MessageHandler(filters.Regex('^دریافت آدرس ولت$'), wallet_address.get_wallet_address))

    # VIP Menu Options
    application.add_handler(MessageHandler(filters.Regex('^پشتیبانی$'), online_support.start_support))
    application.add_handler(MessageHandler(filters.Regex('^ثبت سود و ضرر$'), profit_loss.profit_loss))
    application.add_handler(MessageHandler(filters.Regex('^تمدید اشتراک$'), renew_subscription.renew_subscription))
    application.add_handler(MessageHandler(filters.Regex('^سوالات متداول$'), faq.faq))
    application.add_handler(MessageHandler(filters.Regex('^حساب کاربری$'), results.view_results))
    application.add_handler(MessageHandler(filters.Regex('^قوانین و مقررات$'), regulations.regulations))
    application.add_handler(MessageHandler(filters.Regex('^مشاهده نتایج$'), results.view_results))

    application.add_handler(CommandHandler('menu', menu_command))
    application.add_handler(CommandHandler('user_level', show_user_level))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    stop_event = asyncio.Event()
    await stop_event.wait()

    await application.stop()
    await application.shutdown()


def stop_bot():
    """Stops the bot gracefully."""
    stop_event.set()


if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
