# bot.py
import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ------ Настройки ------
TOKEN = "8477715536:AAEAOTXkXBY93i9iliI7gkXORge4J5L_I8E"  # вставьте токен от BotFather
DATA_FILE = "mangas.json"
ADMIN_IDS = [123456789]  # ваш Telegram user_id

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ------ Утилиты для хранения ------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"titles": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ------ Меню ------
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📚 Каталог", callback_data="catalog"),
        InlineKeyboardButton("💬 О нас", callback_data="about"),
        InlineKeyboardButton("📝 Запрос перевода", callback_data="request"),
    )
    return kb

# ------ Хендлеры ------
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    text = (
        "Привет! 👋\n"
        "Я — бот команды переводчиков манги/манхвы. Выберите действие в меню."
    )
    await message.answer(text, reply_markup=main_menu())

# --- callback для кнопок ---
@dp.callback_query_handler(lambda c: c.data == "about")
async def about_cb(c: types.CallbackQuery):
    await c.answer()
    await bot.send_message(c.from_user.id,
        "Мы переводим мангу и манхву в жанре яой. Переводы делаем с любовью ❤️")

@dp.callback_query_handler(lambda c: c.data == "request")
async def request_cb(c: types.CallbackQuery):
    await c.answer()
    await bot.send_message(c.from_user.id,
        "Чтобы оставить запрос на перевод, напишите название тайтла и ссылку (если есть)")

@dp.callback_query_handler(lambda c: c.data == "catalog")
async def catalog_cb(c: types.CallbackQuery):
    await c.answer()
    data = load_data()
    titles = data.get("titles", [])
    if not titles:
        await bot.send_message(c.from_user.id, "Каталог пуст — скоро добавим новые тайтлы 😊")
        return
    kb = InlineKeyboardMarkup(row_width=1)
    for t in titles:
        kb.add(InlineKeyboardButton(t["name"], callback_data=f"title:{t['id']}"))
    await bot.send_message(c.from_user.id, "Каталог:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("title:"))
async def title_cb(c: types.CallbackQuery):
    await c.answer()
    _, tid = c.data.split(":", 1)
    data = load_data()
    title = next((x for x in data.get("titles", []) if str(x["id"])==tid), None)
    if not title:
        await bot.send_message(c.from_user.id, "Тайтл не найден")
        return
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in title.get("chapters", []):
        kb.add(InlineKeyboardButton(ch["name"], callback_data=f"chapter:{title['id']}:{ch['id']}"))
    await bot.send_message(c.from_user.id, f"Тайтл: {title['name']}\nОписание: {title.get('desc','-')}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("chapter:"))
async def chapter_cb(c: types.CallbackQuery):
    await c.answer()
    _, tid, cid = c.data.split(":")
    data = load_data()
    title = next((x for x in data.get("titles", []) if str(x["id"])==tid), None)
    if not title:
        await bot.send_message(c.from_user.id, "Тайтл не найден")
        return
    chapter = next((ch for ch in title.get("chapters", []) if str(ch["id"])==cid), None)
    if not chapter:
        await bot.send_message(c.from_user.id, "Глава не найдена")
        return
    await bot.send_message(c.from_user.id, f"Глава: {chapter['name']}\n\n{chapter.get('text','(контент отсутствует)')}")

# ------ Админ команды ------
def is_admin(user_id):
    return user_id in ADMIN_IDS

@dp.message_handler(commands=['add_title'])
async def add_title(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    args = message.get_args()
    if '|' not in args:
        await message.reply("Формат: /add_title Название | Короткое описание")
        return
    name, desc = [p.strip() for p in args.split('|',1)]
    data = load_data()
    new_id = max([t['id'] for t in data.get('titles',[])] + [0]) + 1
    data.setdefault("titles", []).append({"id": new_id, "name": name, "desc": desc, "chapters": []})
    save_data(data)
    await message.reply(f"Добавлен тайтл '{name}' (id={new_id})")

@dp.message_handler(commands=['add_chapter'])
async def add_chapter(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    parts = [p.strip() for p in message.get_args().split('|')]
    if len(parts) < 3:
        await message.reply("Формат: /add_chapter TITLE_ID | Имя главы | Текст главы")
        return
    title_id, ch_name, ch_text = parts[0], parts[1], parts[2]
    data = load_data()
    title = next((t for t in data.get("titles",[]) if str(t["id"])==title_id), None)
    if not title:
        await message.reply("Тайтл с таким ID не найден")
        return
    new_ch_id = max([ch['id'] for ch in title.get('chapters',[])] + [0]) + 1
    title.setdefault("chapters", []).append({"id": new_ch_id, "name": ch_name, "text": ch_text})
    save_data(data)
    await message.reply(f"Добавлена глава '{ch_name}' (id={new_ch_id}) в тайтл '{title['name']}'")

# ------ Запуск ------
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
