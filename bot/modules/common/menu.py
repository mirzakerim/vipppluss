from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from utils.database import get_user_level, create_connection, fetch_query

async def show_user_menu(update: Update, context: CallbackContext):
    """
    نمایش منوی کاربری بر اساس سطح دسترسی کاربر.
    """
    user = update.message.from_user
    user_level = get_user_level(user.id)  # دریافت سطح دسترسی کاربر از دیتابیس

    if user_level == 'vip':
        user_menu = [
            ['پشتیبانی', 'ثبت سود و ضرر'],
            ['تمدید اشتراک', 'سوالات متداول'],
            ['حساب کاربری', 'قوانین و مقررات'],
            ['مشاهده نتایج']
        ]
    else:
        user_menu = [
            ['FAQ', 'Support'],
            ['Buy VIP Membership', 'Buy VIP+ Membership'],
            ['View Results', 'Regulations']
        ]

    reply_markup = ReplyKeyboardMarkup(user_menu, one_time_keyboard=True)
    await update.message.reply_text(
        'Here is your menu:',
        reply_markup=reply_markup
    )

def get_user_level(telegram_id):
    """
    دریافت سطح دسترسی کاربر از دیتابیس با استفاده از Telegram ID.
    """
    query = "SELECT user_level FROM users WHERE telegram_id = %s"
    data = (telegram_id,)
    
    with create_connection() as connection:  # استفاده از context manager برای مدیریت اتصال به دیتابیس
        result = fetch_query(connection, query, data)
        
    if result:
        return result[0][0]
    return None
