import asyncio
from aiogram import Bot, Dispatcher, 
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatType
from aiogram.filters import Command
from collections import defaultdict

TOKEN = "SEU_TOKEN_AQUI"

bot = Bot(TOKEN)
dp = Dispatcher()

# -------------------------------
# SISTEMA DE SESSÕES POR USUÁRIO
# -------------------------------
user_sessions = {}
user_tasks = {}

class Session:
    def __init__(self, user_id, query):
        self.user_id = user_id
        self.query = query
        self.selected = None
        self.downloading = False

# -------------------------------
# UTIL
# -------------------------------
def only_group(func):
    async def wrapper(message: Message, *args, **kwargs):
        if message.chat.type == ChatType.PRIVATE:
            return
        return await func(message, *args, **kwargs)
    return wrapper

# -------------------------------
# COMANDO /buscar2
# -------------------------------
@dp.message(Command("buscar2"))
@only_group
async def buscar_manga(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply("Use:\n/buscar2 nome_do_manga")
        return

    query = args[1]
    user_id = message.from_user.id

    # cria sessão
    user_sessions[user_id] = Session(user_id, query)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Baixar PDF", callback_data=f"pdf:{user_id}")],
        [InlineKeyboardButton(text="🖼 Baixar Imagens", callback_data=f"img:{user_id}")]
    ])

    await message.reply(
        f"🔎 Procurando: {query}\nEscolha o formato:",
        reply_markup=keyboard
    )

# -------------------------------
# CANCELAR
# -------------------------------
@dp.message(Command("cancelar"))
@only_group
async def cancelar(message: Message):
    user_id = message.from_user.id

    if user_id in user_tasks:
        user_tasks[user_id].cancel()
        del user_tasks[user_id]

    if user_id in user_sessions:
        del user_sessions[user_id]
        await message.reply("❌ Sua pesquisa foi cancelada.")
    else:
        await message.reply("Você não tem pesquisa ativa.")

# -------------------------------
# DOWNLOAD
# -------------------------------
@dp.callback_query(F.data.startswith(("pdf:", "img:")))
async def escolher_formato(call: CallbackQuery):
    action, owner_id = call.data.split(":")
    owner_id = int(owner_id)

    # bloqueia intrusos
    if call.from_user.id != owner_id:
        await call.answer("Essa pesquisa não é sua.", show_alert=True)
        return

    session = user_sessions.get(owner_id)
    if not session:
        await call.answer("Sessão expirada.")
        return

    if session.downloading:
        await call.answer("Já está baixando.")
        return

    session.selected = action
    session.downloading = True

    msg = await call.message.answer("⏳ Iniciando download...")

    task = asyncio.create_task(simular_download(msg, owner_id))
    user_tasks[owner_id] = task

    await call.answer()

# -------------------------------
# PROGRESSO
# -------------------------------
async def simular_download(msg: Message, user_id: int):
    try:
        for i in range(1, 11):
            await asyncio.sleep(1)
            bar = "█" * i + "░" * (10 - i)
            await msg.edit_text(f"📦 Baixando...\n[{bar}] {i*10}%")

        await msg.edit_text("✅ Download concluído!")

    except asyncio.CancelledError:
        await msg.edit_text("❌ Download cancelado.")
    finally:
        user_sessions.pop(user_id, None)
        user_tasks.pop(user_id, None)

# -------------------------------
# HELP
# -------------------------------
@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.reply(
        "/buscar2 nome → procurar manga\n"
        "/cancelar → cancelar pesquisa"
    )

# -------------------------------
# START
# -------------------------------
async def main():
    print("Bot rodando...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
