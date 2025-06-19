import logging
import requests
import time
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("请设置 BOT_TOKEN 环境变量！")

API_URL = "https://fapi.binance.com/fapi/v1/klines"
CHECK_INTERVAL = 60  # 每60秒检查一次
user_symbols = {}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_kline(symbol):
    try:
        url = f"{API_URL}?symbol={symbol}&interval=1m&limit=2"
        res = requests.get(url, timeout=10)
        data = res.json()
        if isinstance(data, list) and len(data) == 2:
            prev_vol = float(data[0][5])
            curr_vol = float(data[1][5])
            return prev_vol, curr_vol
    except Exception as e:
        logger.warning(f"获取 {symbol} K线失败：{e}")
    return None, None

def volume_monitor(app):
    while True:
        time.sleep(CHECK_INTERVAL)
        for chat_id, symbols in user_symbols.items():
            for symbol in list(symbols):
                prev, curr = get_kline(symbol)
                if prev and curr and prev > 0 and curr > prev * 1.5:
                    growth = (curr / prev - 1) * 100
                    msg = f"🚨 放量提醒：{symbol}\n当前：{curr:.2f} 前一分：{prev:.2f}\n增长率：{growth:.2f}%"
                    try:
                        app.bot.send_message(chat_id=chat_id, text=msg)
                    except Exception as e:
                        logger.warning(f"发送消息失败：{e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_symbols.setdefault(chat_id, set())
    await context.bot.send_message(chat_id=chat_id, text="欢迎使用 Binance 放量监控 Bot。使用 /add SYMBOL 添加监控（如 /add BTCUSDT）")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    symbol = (context.args[0].upper() if context.args else None)
    if not symbol:
        await update.message.reply_text("格式错误，用法：/add BTCUSDT")
        return
    user_symbols.setdefault(chat_id, set()).add(symbol)
    await update.message.reply_text(f"已添加 {symbol} 到监控列表")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    symbol = (context.args[0].upper() if context.args else None)
    if not symbol:
        await update.message.reply_text("格式错误，用法：/remove BTCUSDT")
        return
    if symbol in user_symbols.get(chat_id, set()):
        user_symbols[chat_id].remove(symbol)
        await update.message.reply_text(f"已移除 {symbol}")
    else:
        await update.message.reply_text(f"{symbol} 不在监控列表中")

async def list_symbols(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    symbols = user_symbols.get(chat_id, set())
    if symbols:
        await update.message.reply_text("监控中：" + ", ".join(symbols))
    else:
        await update.message.reply_text("当前没有监控任何交易对。")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("list", list_symbols))

    threading.Thread(target=volume_monitor, args=(app,), daemon=True).start()
    logger.info("Bot 正在运行...")
    app.run_polling()

if __name__ == "__main__":
    main()
