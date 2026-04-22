python

import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import TOKEN
from security import is_admin
from db import init_db, save_excel, search_all, get_stats

init_db()

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 بحث", callback_data="search")],
        [InlineKeyboardButton("📂 رفع ملف", callback_data="upload")],
        [InlineKeyboardButton("📊 تقرير", callback_data="report")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CRM PRO+", reply_markup=menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "search":
        await q.message.reply_text("اكتب كلمة البحث")

    elif q.data == "upload":
        if not is_admin(update.effective_user.id):
            return await q.message.reply_text("غير مصرح")
        await q.message.reply_text("ارسل ملف Excel")

    elif q.data == "report":
        stats = get_stats()
        await q.message.reply_text(str(stats))

async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    file = await update.message.document.get_file()
    path = "data.xlsx"
    await file.download_to_drive(path)

    df = pd.read_excel(path)
    save_excel(df)

    await update.message.reply_text("تم الرفع")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    results = search_all(text)

    if results.empty:
        return await update.message.reply_text("لا توجد نتائج")

    msg = ""
    for _, row in results.iterrows():
        msg += "\n".join([f"{k}: {v}" for k,v in row.items()])
        msg += "\n-----\n"

    await update.message.reply_text(msg[:4000])

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.Document.ALL, file_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
