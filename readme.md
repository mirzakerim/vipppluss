README.md
markdown
Copy code
# Modular Telegram Bot - Version 2

این نسخه از ربات تلگرام ماژولار شامل امکانات زیر است:
- ثبت‌نام کاربران جدید
- منوی کاربران با سطوح مختلف دسترسی (کاربر عادی، VIP، مدیر)
- مدیریت درخواست‌های پشتیبانی
- مشاهده نتایج، خرید عضویت VIP و VIP+
- دریافت لیست بروکرها و آدرس ولت
- بازگشت به منوی اصلی از هر ماژول

## ساختار پروژه
my_modular_bot/
│
├── main.py
├── config.py
├── .env
├── README.md

├── requirements.txt
│
├── bot/
│   ├── main_bot.py
│   ├── modules/
│   │   ├── common/
│   │   │   ├── faq.py
│   │   │   ├── regulations.py
│   │   │   ├── menu.py
│   │   │   ├── results.py
│   │   │   ├── brokers_list.py
│   │   │   ├── wallet_address.py
│   │   ├── user/
│   │   │   ├── register.py
│   │   │   ├── buy-vip.py
│   │   │   ├── buy-vipplus.py
│   │   │   ├── send_receipt.py
│   │   ├── vip/
│   │   │   ├── profit_loss.py
│   │   │   ├── renew_subscription.py
│   │   │   ├── send_receipt.py
│   │   │   ├── acc.py
│   │   ├── support/
│   │       ├── online_support.py
│
└── utils/
    ├── database.py
    ├── logger.py


## راه‌اندازی پروژه

### پیش‌نیازها
- Python 3.12
- pip

### نصب وابستگی‌ها

pip install -r requirements.txt
اجرای ربات
اطمینان حاصل کنید که TOKEN و اطلاعات اتصال به دیتابیس در فایل config.py به درستی تنظیم شده‌اند.

اجرای ربات:


python main.py
توضیحات ماژول‌ها
bot/main_bot.py
فایل اصلی ربات که وظیفه راه‌اندازی و مدیریت هندلرها را دارد.

bot/modules/user/register.py
ماژول ثبت‌نام کاربران جدید. این ماژول شامل مراحل مختلفی برای جمع‌آوری اطلاعات کاربر است.

bot/modules/common/menu.py
ماژول نمایش منوی اصلی کاربران. شامل دکمه‌های مختلف برای دسترسی به امکانات ربات.

bot/modules/common/results.py
ماژول نمایش نتایج. پیام مربوط به نمایش نتایج و لینک کانال نمایش داده می‌شود.

bot/modules/user/buy-vip.py
ماژول خرید عضویت VIP. پیام خوشامدگویی و اطلاعات عضویت نمایش داده می‌شود و دکمه‌های مختلف برای دریافت اطلاعات بیشتر و ارسال رسید وجود دارد.

bot/modules/user/buy-vipplus.py
ماژول خرید عضویت plusVIP. پیام خوشامدگویی و اطلاعات عضویت نمایش داده می‌شود و دکمه‌های مختلف برای دریافت اطلاعات بیشتر و ارسال رسید وجود دارد.

bot/modules/common/brokers_list.py
ماژول دریافت لیست بروکرها. پیام مربوط به لیست بروکرها نمایش داده می‌شود و دکمه بازگشت به منوی قبلی موجود است.

bot/modules/common/wallet_address.py
ماژول دریافت آدرس ولت. پیام مربوط به آدرس ولت نمایش داده می‌شود و دکمه بازگشت به منوی قبلی موجود است.


bot/modules/support/online_support.py
ماژول پشتیبانی آنلاین. کاربران می‌توانند سوالات خود را مطرح کنند و به دپارتمان‌های مختلف ارسال کنند.

utils/database.py
ماژول مدیریت اتصال به دیتابیس و اجرای کوئری‌ها.

