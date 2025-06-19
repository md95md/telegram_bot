import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler

import os

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

user_states = {}

print(f"BOT TOKEN = {TELEGRAM_BOT_TOKEN}")

MOOD_TEMPLATES = {
    "melancholic": "A symbolic acrylic painting with bold brush strokes and clean, bright colors.\nThe scene expresses a sense of melancholy with a focus on {subject} — {user_input}.\nMuted tones and a quiet, introspective atmosphere. Format: 1:1. Palette: {palette}.",

    "joyful": "A symbolic acrylic painting with bold brush strokes and clean, bright colors.\nThe scene conveys joy and celebration through {subject} — {user_input}.\nVibrant hues and playful brush patterns. Format: 1:1. Palette: {palette}.",

    "aggressive": "A symbolic acrylic painting with bold brush strokes and clean, bright colors.\nThe scene bursts with intensity and anger, focused on {subject} — {user_input}.\nSharp contrasts and chaotic textures. Format: 1:1. Palette: {palette}.",

    "romantic": "A symbolic acrylic painting with bold brush strokes and clean, bright colors.\nThe scene radiates love and intimacy using {subject} — {user_input}.\nSoft glows and warm tones. Format: 1:1. Palette: {palette}.",

    "spiritual": "A symbolic acrylic painting with bold brush strokes and clean, bright colors.\nThe scene evokes a spiritual or meditative state through {subject} — {user_input}.\nFloating forms and tranquil gradients. Format: 1:1. Palette: {palette}.",

    "calm": "A symbolic acrylic painting with bold brush strokes and clean, bright colors.\nThe scene captures peacefulness with {subject} — {user_input}.\nBalanced shapes and gentle lighting. Format: 1:1. Palette: {palette}."
}

async def prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = {"state": "choosing_mood"}
    keyboard = [
        [InlineKeyboardButton("\uD83C\uDF27️ Меланхоличное", callback_data="mood_melancholic")],
        [InlineKeyboardButton("\uD83C\uDF1E Радостное", callback_data="mood_joyful")],
        [InlineKeyboardButton("\uD83D\uDD25 Агрессивное", callback_data="mood_aggressive")],
        [InlineKeyboardButton("\uD83D\uDC98 Влюбленность", callback_data="mood_romantic")],
        [InlineKeyboardButton("\uD83E\uDDE8 Духовное", callback_data="mood_spiritual")],
        [InlineKeyboardButton("\uD83C\uDF3F Спокойное", callback_data="mood_calm")]
    ]
    await update.message.reply_text("Какое настроение ты хочешь выразить в изображении?", reply_markup=InlineKeyboardMarkup(keyboard))

async def mood_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    mood_key = query.data.replace("mood_", "")
    user_states[user_id] = {"state": "choosing_palette", "mood": mood_key}

    keyboard = [
        [InlineKeyboardButton("Яркая", callback_data="palette_bright")],
        [InlineKeyboardButton("Пастельная", callback_data="palette_pastel")],
        [InlineKeyboardButton("Психоделическая", callback_data="palette_psychedelic")],
        [InlineKeyboardButton("Контрастная", callback_data="palette_contrast")],
        [InlineKeyboardButton("Однотонная", callback_data="palette_monochrome")],
        [InlineKeyboardButton("Черно-белая", callback_data="palette_bw")]
    ]
    await query.message.reply_text("Выберите цветовую палитру:", reply_markup=InlineKeyboardMarkup(keyboard))

async def palette_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    palette = query.data.replace("palette_", "")
    user_states[user_id]["palette"] = palette
    user_states[user_id]["state"] = "choosing_subject"

    keyboard = [
        [InlineKeyboardButton("👥 Люди", callback_data="subject_people")],
        [InlineKeyboardButton("🐾 Животные", callback_data="subject_animals")],
        [InlineKeyboardButton("🌄 Пейзаж", callback_data="subject_landscape")],
        [InlineKeyboardButton("🖨 Абстракция", callback_data="subject_abstract")],
        [InlineKeyboardButton("📖 Сюжет", callback_data="subject_narrative")],
        [InlineKeyboardButton("🌺 Цветы", callback_data="subject_flowers")]
    ]
    await query.message.reply_text("Что вы хотите видеть на картине?", reply_markup=InlineKeyboardMarkup(keyboard))

async def subject_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    subject = query.data.replace("subject_", "")
    user_states[user_id]["subject"] = subject
    user_states[user_id]["state"] = "waiting_for_description"
    await query.message.reply_text("Добавьте еще несколько слов, что хотите увидеть на картине:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "/prompt":
        return

    if user_id in user_states:
        state_info = user_states[user_id]
        if state_info["state"] == "waiting_for_description":
            mood = state_info["mood"]
            palette = state_info["palette"]
            subject = state_info["subject"]
            styled_prompt = MOOD_TEMPLATES[mood].format(user_input=text, palette=palette, subject=subject)
            await update.message.reply_text(f"🎯 Prompt:\n{styled_prompt}\n\nСкопируй промпт и отправь в DALL·E: https://openai.com/dall-e")
            del user_states[user_id]
            return

    if chat_type == "private":
        await update.message.reply_text("👋 Привет! Чтобы начать, напиши команду /prompt.")
    else:
        return

    await update.message.reply_text("Type /prompt to start.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("prompt", prompt_command))
    app.add_handler(CallbackQueryHandler(mood_chosen, pattern="^mood_"))
    app.add_handler(CallbackQueryHandler(palette_chosen, pattern="^palette_"))
    app.add_handler(CallbackQueryHandler(subject_chosen, pattern="^subject_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
