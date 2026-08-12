import os
import sys
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ایمپورت کردن مدیریت ربات که قبلاً ساختیم
from bot_manager import TradingBotManager

# ==========================================
# تنظیمات کلیدها (حتماً توکن ربات تلگرام خود را از @BotFather بگیرید)
# ==========================================
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
NOBITEX_API_KEY = 'YOUR_NOBITEX_API_KEY'
NOBITEX_SECRET_KEY = 'YOUR_NOBITEX_SECRET_KEY'

# ساخت یک نمونه از مدیریت معاملات
print("Initializing Bot Manager...")
bot_manager = TradingBotManager(api_key=NOBITEX_API_KEY, secret=NOBITEX_SECRET_KEY)

# ==========================================
# ساخت دکمه‌های شیشه‌ای (Inline Keyboards)
# ==========================================
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 موجودی حساب", callback_data='balance')],
        [InlineKeyboardButton("📋 سفارشات باز", callback_data='open_orders'),
         InlineKeyboardButton("❌ بستن همه سفارشات", callback_data='cancel_all')],
        [InlineKeyboardButton("📖 تاریخچه و سود/زیان", callback_data='history_pnl')],
        [InlineKeyboardButton("🛒 ثبت سفارش (راهنما)", callback_data='help_order')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# دستورات ربات
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع ربات و نمایش منوی اصلی"""
    welcome_msg = "👋 به ربات معامله‌گر نوبیتکس خوش آمدید!\nیک گزینه را انتخاب کنید:"
    await update.message.reply_text(welcome_msg, reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """هندلر اصلی برای کلیک روی دکمه‌ها"""
    query = update.callback_query
    await query.answer() # پاسخ به کلیک کاربر (برای رفع لودینگ دکمه)
    
    data = query.data
    
    if data == 'balance':
        await query.edit_message_text("⏳ در حال دریافت موجودی...")
        try:
            balance = bot_manager.exchange.fetch_balance()
            non_zero = {k: v for k, v in balance.items() if k != 'info' and isinstance(v, dict) and v.get('total') not in [None, 0]}
            if not non_zero:
                msg = "موجودی غیر صصفر یافت نشد."
            else:
                msg = "💰 *موجودی شما:*\n\n"
                for cur, val in non_zero.items():
                    msg += f"  `{cur}`: Free: `{val.get('free')}` | Total: `{val.get('total')}`\n"
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())
        except Exception as e:
            await query.edit_message_text(f"❌ خطا: {e}", reply_markup=get_main_menu())

    elif data == 'open_orders':
        await query.edit_message_text("⏳ در حال دریافت سفارشات باز...")
        try:
            orders = bot_manager.get_open_orders()
            if not orders:
                msg = "📋 شما سفارش باز ندارید."
            else:
                msg = "📋 *سفارشات باز:*\n\n"
                for o in orders[:5]: # فقط 5 مورد اول
                    msg += f"🆔 `{o['id']}`\n  `{o['symbol']}` | {o['side']} | Amount: `{o['amount']}`\n\n"
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())
        except Exception as e:
            await query.edit_message_text(f"❌ خطا: {e}", reply_markup=get_main_menu())

    elif data == 'cancel_all':
        await query.edit_message_text("⏳ در حال بستن تمام سفارشات باز...")
        success = bot_manager.cancel_all_open_orders()
        if success:
            await query.edit_message_text("✅ تمام سفارشات باز با موفقیت بسته شدند.", reply_markup=get_main_menu())
        else:
            await query.edit_message_text("❌ خطا در بستن سفارشات.", reply_markup=get_main_menu())

    elif data == 'history_pnl':
        await query.edit_message_text("⏳ در حال محاسبه سود و زیان...")
        try:
            trades = bot_manager.get_trade_history(limit=50)
            if not trades:
                msg = "📖 تاریخچه معاملاتی یافت نشد."
            else:
                # برای تلگرام، خروجی PnL را کوتاه می‌کنیم
                pnl_data = bot_manager.calculate_pnl(trades)
                msg = "📊 *خلاصه سود و زیان (Cash Flow):*\n\n"
                for currency, val in pnl_data['total'].items():
                    msg += f"  `{currency}`: `{val:,.2f}`\n"
                msg += "\nبرای جزئیات روزانه و ماهانه، به لاگ‌های ترمینال نگاه کنید."
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())
        except Exception as e:
            await query.edit_message_text(f"❌ خطا: {e}", reply_markup=get_main_menu())

    elif data == 'help_order':
        msg = (
            "🛒 *راهنمای ثبت سفارش:*\n\n"
            "برای ثبت سفارش، از دستورات زیر استفاده کنید:\n\n"
            "خرید: `/buy SYMBOL AMOUNT PRICE`\n"
            "مثال: `/buy BTC/USDT 0.001 60000`\n\n"
            "فروش: `/sell SYMBOL AMOUNT PRICE`\n"
            "مثال: `/sell BTC/USDT 0.001 65000`"
        )
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        symbol = context.args[0].upper()
        amount = float(context.args[1])
        price = float(context.args[2])
        
        msg = await update.message.reply_text(f"⏳ در حال ثبت سفارش خرید {amount} {symbol} با قیمت {price}...")
        order = bot_manager.place_order(symbol, 'buy', amount, price)
        
        if order:
            await msg.edit_text(f"✅ سفارش خرید ثبت شد!\n🆔 شناسه: `{order.get('id')}`", parse_mode='Markdown')
        else:
            await msg.edit_text("❌ ثبت سفارش ناموفق بود.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ فرمت اشتباه است. مثال:\n`/buy BTC/USDT 0.001 60000`", parse_mode='Markdown')

async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        symbol = context.args[0].upper()
        amount = float(context.args[1])
        price = float(context.args[2])
        
        msg = await update.message.reply_text(f"⏳ در حال ثبت سفارش فروش {amount} {symbol} با قیمت {price}...")
        order = bot_manager.place_order(symbol, 'sell', amount, price)
        
        if order:
            await msg.edit_text(f"✅ سفارش فروش ثبت شد!\n🆔 شناسه: `{order.get('id')}`", parse_mode='Markdown')
        else:
            await msg.edit_text("❌ ثبت سفارش ناموفق بود.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ فرمت اشتباه است. مثال:\n`/sell BTC/USDT 0.001 60000`", parse_mode='Markdown')

# ==========================================
# راه‌اندازی ربات
# ==========================================
def main() -> None:
    print("🤖 Telegram Bot is starting...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy_command))
    application.add_handler(CommandHandler("sell", sell_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()