from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from utils.database import get_user_level

menu_translation = {
    'FAQ': 'سوالات متداول ❓',
    'Support': 'پشتیبانی 🛠',
    'Buy VIP Membership': 'خرید عضویت VIP 💳',
    'Buy VIP+ Membership': 'خرید عضویت VIP+ 💎',
    'View Results': 'مشاهده نتایج 📊',
    'Regulations': 'قوانین و مقررات 📜',
    'دریافت لیست بروکرها': 'دریافت لیست بروکرها 📃',
    'دریافت آدرس ولت': 'دریافت آدرس ولت 💼',
    'پشتیبانی': 'پشتیبانی 🛠',
    'ثبت سود و ضرر': 'ثبت سود و ضرر 📈📉',
    'تمدید اشتراک': 'تمدید اشتراک 🔄',
    'سوالات متداول': 'سوالات متداول ❓',
    'حساب کاربری': 'حساب کاربری 🧾',
    'قوانین و مقررات': 'قوانین و مقررات 📜',
    'مشاهده نتایج': 'مشاهده نتایج 📊'
}

async def show_user_menu(update: Update, context: CallbackContext):
    """
    نمایش منوی کاربری بر اساس سطح دسترسی کاربر.
    """
    user = update.message.from_user
    user_level = get_user_level(user.id)  # دریافت سطح دسترسی کاربر از دیتابیس

    if user_level == 'vip':
        user_menu = [
            [menu_translation['پشتیبانی'], menu_translation['ثبت سود و ضرر']],
            [menu_translation['تمدید اشتراک'], menu_translation['سوالات متداول']],
            [menu_translation['حساب کاربری'], menu_translation['قوانین و مقررات']],
            [menu_translation['مشاهده نتایج']]
        ]
    else:
        user_menu = [
            [menu_translation['FAQ'], menu_translation['Support']],
            [menu_translation['Buy VIP Membership'], menu_translation['Buy VIP+ Membership']],
            [menu_translation['View Results'], menu_translation['Regulations']]
        ]

    reply_markup = ReplyKeyboardMarkup(user_menu, one_time_keyboard=True)
    await update.message.reply_text(
        'Here is your menu:',
        reply_markup=reply_markup
    )
