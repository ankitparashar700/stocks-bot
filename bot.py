import logging
import yfinance as yf
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your actual bot token
TELEGRAM_BOT_TOKEN = "AAGW0RB2UjR4VQugiz3BpxY6XLjbyaNmBK0"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Stock Analysis Logic ---
def get_stock_recommendation(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")

        if hist.empty:
            return f"No data found for {ticker.upper()}"

        closing_prices = hist['Close']
        sma_10 = closing_prices.rolling(window=10).mean()
        sma_20 = closing_prices.rolling(window=20).mean()

        latest_price = closing_prices.iloc[-1]
        sma10 = sma_10.iloc[-1]
        sma20 = sma_20.iloc[-1]

        recommendation = ""
        if sma10 > sma20:
            recommendation = "📈 Recommendation: BUY (Uptrend detected)"
        elif sma10 < sma20:
            recommendation = "📉 Recommendation: SELL (Downtrend detected)"
        else:
            recommendation = "🤔 Recommendation: HOLD (No clear signal)"

        return (
            f"Stock: {ticker.upper()}\n"
            f"Latest Price: ${latest_price:.2f}\n"
            f"SMA 10: ${sma10:.2f}, SMA 20: ${sma20:.2f}\n"
            f"{recommendation}"
        )

    except Exception as e:
        return f"⚠️ Error fetching data for {ticker.upper()}: {str(e)}"

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to StockBot!\n\nUse /recommend <ticker> to get a stock recommendation.\nExample: /recommend AAPL"
    )

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide a stock ticker. Example: /recommend TSLA")
        return

    ticker = context.args[0].upper()
    result = get_stock_recommendation(ticker)
    await update.message.reply_text(result)

# --- Main Function ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recommend", recommend))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
