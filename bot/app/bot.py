import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .config import settings
from .keyboards import main_menu

API_URL = settings.api_internal_url.rstrip("/")
BOT_TOKEN = settings.bot_token

class LeadFSM(StatesGroup):
    name = State()
    phone = State()
    city = State()
    work_type = State()
    budget = State()
    description = State()
    photos = State()

class ContractorFSM(StatesGroup):
    name = State()
    phone = State()
    city = State()
    specialization = State()
    experience = State()
    description = State()

async def api_get(path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL + path) as resp:
            if resp.status != 200:
                raise RuntimeError(await resp.text())
            return await resp.json()

async def api_post_lead(payload: dict):
    headers = {"X-Bot-Token": BOT_TOKEN, "Content-Type":"application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + "/api/bot/leads", json=payload, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(await resp.text())
            return await resp.json()

def admin_ids():
    return settings.admin_ids

async def notify_admins(bot: Bot, text: str):
    for aid in admin_ids():
        try:
            await bot.send_message(aid, text)
        except Exception:
            pass

async def start_handler(message: Message):
    await message.answer(
        "БригАдрес 🧩\n\n"
        "Это демонстрационный бот + WebApp. Он показывает:\n"
        "• WebApp внутри Telegram\n"
        "• заявки в базу + админка\n"
        "• документы и FAQ\n\n"
        "Выбери действие ниже 👇",
        reply_markup=main_menu()
    )

async def docs_handler(cb: CallbackQuery):
    data = await api_get("/api/content/documents")
    lines = ["🧾 Документы:"]
    for d in data:
        # public link from API
        url = settings.public_base_url.rstrip("/") + d["url"]
        lines.append(f"• {d['title']}: {url}")
    await cb.message.answer("\n".join(lines))
    await cb.answer()

async def faq_handler(cb: CallbackQuery):
    data = await api_get("/api/content/faq")
    text = "❓ FAQ (кратко):\n\n"
    for i, item in enumerate(data[:5], start=1):
        text += f"{i}) {item['question']}\n"
    text += "\nПолные ответы — в WebApp."
    await cb.message.answer(text)
    await cb.answer()

async def lead_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(LeadFSM.name)
    await cb.message.answer("🛠️ Заявка на ремонт.\nКак тебя зовут?")
    await cb.answer()

async def contractor_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ContractorFSM.name)
    await cb.message.answer("👷 Заявка подрядчика.\nКак вас зовут / как называется бригада?")
    await cb.answer()

async def lead_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(LeadFSM.phone)
    await message.answer("Телефон для связи?")

async def lead_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(LeadFSM.city)
    await message.answer("Город?")

async def lead_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await state.set_state(LeadFSM.work_type)
    await message.answer("Тип работ (например: плитка/электрика/ремонт под ключ)?")

async def lead_work(message: Message, state: FSMContext):
    await state.update_data(work_type=message.text.strip())
    await state.set_state(LeadFSM.budget)
    await message.answer("Бюджет (если есть ориентир)?")

async def lead_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text.strip())
    await state.set_state(LeadFSM.description)
    await message.answer("Коротко опиши задачу (что нужно сделать, сроки, нюансы).")

async def lead_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(LeadFSM.photos)
    await message.answer("Если есть фото/скрины — отправь их сообщением (можно несколько).\nКогда закончишь — напиши: ГОТОВО")

async def lead_photos(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    attachments = data.get("attachments", [])

    if message.photo:
        attachments.append(message.photo[-1].file_id)
        await state.update_data(attachments=attachments)
        await message.answer("Фото добавлено. Ещё? Если всё — напиши: ГОТОВО")
        return

    if message.text and message.text.strip().lower() == "готово":
        payload = {
            "lead_type": "client_request",
            "name": data.get("name"),
            "phone": data.get("phone"),
            "city": data.get("city"),
            "work_type": data.get("work_type"),
            "budget": data.get("budget"),
            "description": f"{data.get('description','')}\n\n[Telegram user: @{message.from_user.username or 'no_username'} | id={message.from_user.id}]",
            "attachments": attachments
        }
        created = await api_post_lead(payload)
        await message.answer(f"✅ Заявка создана: #{created['id']}\nСтатус: {created['status']}\n\nСпасибо! В демо-версии менеджер не отвечает, но всё уходит в базу.")
        await notify_admins(bot, f"🆕 Новая заявка (клиент) #{created['id']}\nГород: {payload['city']}\nРаботы: {payload['work_type']}\nТелефон: {payload['phone']}")
        await state.clear()
        return

    await message.answer("Пришли фото или напиши ГОТОВО.")

# Contractor flow
async def c_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(ContractorFSM.phone)
    await message.answer("Телефон?")

async def c_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(ContractorFSM.city)
    await message.answer("Город / регион?")

async def c_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await state.set_state(ContractorFSM.specialization)
    await message.answer("Специализация (например: ремонт квартир / электрика / плитка)?")

async def c_spec(message: Message, state: FSMContext):
    await state.update_data(specialization=message.text.strip())
    await state.set_state(ContractorFSM.experience)
    await message.answer("Опыт (лет) / сколько объектов?")

async def c_exp(message: Message, state: FSMContext):
    await state.update_data(experience=message.text.strip())
    await state.set_state(ContractorFSM.description)
    await message.answer("Коротко о вашей бригаде (команда, фото/портфолио ссылкой, условия).")

async def c_desc(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    payload = {
        "lead_type": "contractor_application",
        "name": data.get("name"),
        "phone": data.get("phone"),
        "city": data.get("city"),
        "work_type": data.get("specialization"),
        "budget": data.get("experience"),
        "description": f"{message.text.strip()}\n\n[Telegram user: @{message.from_user.username or 'no_username'} | id={message.from_user.id}]",
        "attachments": []
    }
    created = await api_post_lead(payload)
    await message.answer(f"✅ Заявка подрядчика создана: #{created['id']}\nСпасибо! Мы свяжемся (в демо — просто запись в базу).")
    await notify_admins(bot, f"🆕 Новая заявка (подрядчик) #{created['id']}\nГород: {payload['city']}\nСпец: {payload['work_type']}\nТелефон: {payload['phone']}")
    await state.clear()

def setup(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())

    dp.callback_query.register(docs_handler, F.data == "docs")
    dp.callback_query.register(faq_handler, F.data == "faq")
    dp.callback_query.register(lead_start, F.data == "lead")
    dp.callback_query.register(contractor_start, F.data == "contractor")

    dp.message.register(lead_name, LeadFSM.name)
    dp.message.register(lead_phone, LeadFSM.phone)
    dp.message.register(lead_city, LeadFSM.city)
    dp.message.register(lead_work, LeadFSM.work_type)
    dp.message.register(lead_budget, LeadFSM.budget)
    dp.message.register(lead_desc, LeadFSM.description)
    dp.message.register(lead_photos, LeadFSM.photos)

    dp.message.register(c_name, ContractorFSM.name)
    dp.message.register(c_phone, ContractorFSM.phone)
    dp.message.register(c_city, ContractorFSM.city)
    dp.message.register(c_spec, ContractorFSM.specialization)
    dp.message.register(c_exp, ContractorFSM.experience)
    dp.message.register(c_desc, ContractorFSM.description)

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    setup(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
