import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ================== CONFIG داخل الملف ==================
TOKEN = "8742647529:AAGIFR4b0IRaTHLxnH5-L5IEoM2PYizaSFo"
ADMIN_ID = 951388391
# =======================================================

from db import init_db, save_excel, search_all, get_stats

init_db()

# ---------------- MENU ----------------
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 بحث", callback_data="search")],
        [InlineKeyboardButton("📂 رفع ملف", callback_data="upload")],
        [InlineKeyboardButton("📊 تقرير", callback_data="report")]
    ])

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 CRM BOT جاهز", reply_markup=menu())

# ---------------- BUTTONS ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "search":
        await q.message.reply_text("🔍 اكتب كلمة البحث")

    elif q.data == "upload":
        if update.effective_user.id != ADMIN_ID:
            return await q.message.reply_text("❌ غير مصرح")
        await q.message.reply_text("📂 أرسل ملف Excel")

    elif q.data == "report":
        stats = get_stats()
        await q.message.reply_text(f"📊 التقرير:\n{stats}")

# ---------------- FILE UPLOAD ----------------
async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    file = await update.message.document.get_file()
    path = "data.xlsx"
    await file.download_to_drive(path)

    df = pd.read_excel(path)
    save_excel(df)

    await update.message.reply_text("✅ تم رفع الملف بنجاح")

# ---------------- SEARCH ----------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    results = search_all(text)

    if results.empty:
        await update.message.reply_text("❌ لا توجد نتائج")
        return

    msg = "📌 النتائج:\n\n"

    for _, row in results.iterrows():
        for k, v in row.items():
            msg += f"{k}: {v}\n"
        msg += "-----------------\n"

    await update.message.reply_text(msg[:4000])

# ---------------- BOT START ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.Document.ALL, file_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
