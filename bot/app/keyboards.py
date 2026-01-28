from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from .config import settings

def main_menu() -> InlineKeyboardMarkup:
    webapp_url = settings.public_base_url.rstrip("/") + "/webapp/"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть WebApp (демо)", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton(text="🧾 Документы (PDF)", callback_data="docs")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton(text="🛠️ Оставить заявку (в боте)", callback_data="lead")],
        [InlineKeyboardButton(text="👷 Стать подрядчиком (в боте)", callback_data="contractor")],
    ])
