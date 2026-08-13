import os
import sys
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Import the bot manager we created previously
from bot_manager import TradingBotManager

# ==========================================
# Key settings (Make sure to get your Telegram bot token from @BotFather)
# ==========================================
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
NOBITEX_API_KEY = 'YOUR_NOBITEX_API_KEY'
NOBITEX_SECRET_KEY = 'YOUR_NOBITEX_SECRET_KEY'

# Instantiate the trading bot manager
print("Initializing Bot Manager...")
bot_manager = TradingBotManager(api_key=NOBITEX_API_KEY, secret=NOBITEX_SECRET_KEY)

# ==========================================
# Create Inline Keyboards
# ==========================================
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 Account Balance", callback_data='balance')],
        [InlineKeyboardButton("📋 Open Orders", callback_data='open_orders'),
         InlineKeyboardButton("❌ Cancel All Orders", callback_data='cancel_all')],
        [InlineKeyboardButton("📖 Trade History & PnL", callback_data='history_pnl')],
        [InlineKeyboardButton("🛒 Place Order (Help)", callback_data='help_order')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# Bot Commands
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the bot and show the main menu"""
    welcome_msg = "👋 Welcome to the Nobitex Trading Bot!\nPlease select an option:"
    await update.message.reply_text(welcome_msg, reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main handler for button clicks"""
    query = update.callback_query
    await query.answer() # Answer the user's click (to remove button loading)
    
    data = query.data
    
    if data == 'balance':
        await query.edit_message_text("⏳ Fetching balance...")
        try:
            balance = bot_manager.exchange.fetch_balance()
            non_zero = {k: v for k, v in balance.items() if k != 'info' and isinstance(v, dict) and v.get('total') not in [None, 0]}
            if not non_zero:
                msg = "No non-zero balance found."
            else:
                msg = "💰 *Your Balance:*\n\n"
                for cur, val in non_zero.items():
                    msg += f"  `{cur}`: Free: `{val.get('free')}` | Total: `{val.get('total')}`\n"
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", reply_markup=get_main_menu())

    elif data == 'open_orders':
        await query.edit_message_text("⏳ Fetching open orders...")
        try:
            orders = bot_manager.get_open_orders()
            if not orders:
                msg = "📋 You have no open orders."
            else:
                msg = "📋 *Open Orders:*\n\n"
                for o in orders[:5]: # Only the first 5 items
                    msg += f"🆔 `{o['id']}`\n  `{o['symbol']}` | {o['side']} | Amount: `{o['amount']}`\n\n"
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", reply_markup=get_main_menu())

    elif data == 'cancel_all':
        await query.edit_message_text("⏳ Cancelling all open orders...")
        success = bot_manager.cancel_all_open_orders()
        if success:
            await query.edit_message_text("✅ All open orders successfully cancelled.", reply_markup=get_main_menu())
        else:
            await query.edit_message_text("❌ Error cancelling orders.", reply_markup=get_main_menu())

    elif data == 'history_pnl':
        await query.edit_message_text("⏳ Calculating PnL...")
        try:
            trades = bot_manager.get_trade_history(limit=50)
            if not trades:
                msg = "📖 No trade history found."
            else:
                # Shorten the PnL output for Telegram
                pnl_data = bot_manager.calculate_pnl(trades)
                msg = "📊 *PnL Summary (Cash Flow):*\n\n"
                for currency, val in pnl_data['total'].items():
                    msg += f"  `{currency}`: `{val:,.2f}`\n"
                msg += "\nFor daily and monthly details, check the terminal logs."
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}", reply_markup=get_main_menu())

    elif data == 'help_order':
        msg = (
            "🛒 *Order Placement Guide:*\n\n"
            "To place an order, use the following commands:\n\n"
            "Buy: `/buy SYMBOL AMOUNT PRICE`\n"
            "Example: `/buy BTC/USDT 0.001 60000`\n\n"
            "Sell: `/sell SYMBOL AMOUNT PRICE`\n"
            "Example: `/sell BTC/USDT 0.001 65000`"
        )
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_main_menu())

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        symbol = context.args[0].upper()
        amount = float(context.args[1])
        price = float(context.args[2])
        
        msg = await update.message.reply_text(f"⏳ Placing buy order for {amount} {symbol} at price {price}...")
        order = bot_manager.place_order(symbol, 'buy', amount, price)
        
        if order:
            await msg.edit_text(f"✅ Buy order placed!\n🆔 ID: `{order.get('id')}`", parse_mode='Markdown')
        else:
            await msg.edit_text("❌ Order placement failed.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid format. Example:\n`/buy BTC/USDT 0.001 60000`", parse_mode='Markdown')

async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        symbol = context.args[0].upper()
        amount = float(context.args[1])
        price = float(context.args[2])
        
        msg = await update.message.reply_text(f"⏳ Placing sell order for {amount} {symbol} at price {price}...")
        order = bot_manager.place_order(symbol, 'sell', amount, price)
        
        if order:
            await msg.edit_text(f"✅ Sell order placed!\n🆔 ID: `{order.get('id')}`", parse_mode='Markdown')
        else:
            await msg.edit_text("❌ Order placement failed.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid format. Example:\n`/sell BTC/USDT 0.001 60000`", parse_mode='Markdown')

# ==========================================
# Bot Setup
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