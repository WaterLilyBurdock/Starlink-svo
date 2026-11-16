# bot.py
# pip install python-telegram-bot aiohttp
# Запуск: python bot.py

import logging
import os
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ========== НАСТРОЙКИ ==========
# Токен берется из переменной окружения BOT_TOKEN (на Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ID получателя заявок (ID клиента)
ADMIN_CHAT_ID = 7281558645  

# Ссылка на сайт (для кнопки "Открыть на сайте")
LEGAL_URL = "https://waterlilyburdock.github.io/Starlink-svo/"

PAYMENT_WORKER_URL = "" 

# ========== ДАННЫЕ УСЛУГ ==========
SERVICES = {
    "svc_mini": {
        "title": "Starlink Mini V5",
        "desc": (
            "Компактный терминал весом менее 1.16 кг.\n"
            "Скорость до 100 Mbps, задержка до 23 ms.\n"
            "Питание от DC / PowerBank (USB-C PD).\n"
            "Защита IP67, работа от −30 °C до +50 °C.\n\n"
            "Цена по запросу."
        ),
        "price": "190000.00",
    },
    "svc_v3": {
        "title": "Starlink V3 / V4",
        "desc": (
            "Стационарная версия. Скорость до 250 Мбит/сек.\n"
            "Wi-Fi 6, Tri-Band, MU-MIMO 4×4, до 256 абонентов.\n"
            "Два LAN-порта Ethernet.\n"
            "Защита IP67, работа от −30 °C до +50 °C.\n\n"
            "Цена по запросу."
        ),
        "price": "190000.00",
    },
    "svc_consult": {
        "title": "Консультация",
        "desc": (
            "Ответим на вопросы по активации, оплате тарифа "
            "и использованию оборудования.\n\n"
            "Наши контакты:\n"
            "📞 +7 (980) 475-95-51\n"
            "✉️ svoilink@mail.ru\n"
            "💬 @svoi_activ"
        ),
        "price": None,
    },
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ========== ХЕЛПЕРЫ ==========
async def create_payment(amount: str, description: str):
    if not PAYMENT_WORKER_URL:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                PAYMENT_WORKER_URL,
                json={"amount": amount, "description": description},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Worker вернул {resp.status}")
                    return None
                data = await resp.json()
                return data.get("url")
    except Exception as e:
        logger.error(f"Ошибка вызова платёжного воркера: {e}")
        return None


# ========== ХЕНДЛЕРЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Список услуг", callback_data="services")],
        [InlineKeyboardButton("Политика конфиденциальности", callback_data="legal_privacy")],
        [InlineKeyboardButton("Пользовательское соглашение", callback_data="legal_terms")],
        [InlineKeyboardButton("Открыть на сайте", url=LEGAL_URL)]
    ]
    text = (
        "Здравствуйте! Это официальный бот <b>СВОЙLINK</b>.\n\n"
        "Здесь вы можете выбрать комплект Starlink "
        "и оставить заявку на покупку."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def show_legal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "legal_privacy":
        text = (
            "<b>Политика конфиденциальности</b>\n\n"
            "Мы собираем ваши данные (имя, телефон), только когда вы оставляете заявку. "
            "Эти данные используются исключительно для связи с вами по вопросам заказа.\n\n"
            "Данные не передаются третьим лицам, за исключением случаев, предусмотренных законом. "
            "Мы храним их не дольше, чем это необходимо для целей обработки.\n\n"
            "Вы можете запросить удаление своих данных, написав нам на svoilink@mail.ru"
        )
    else:
        text = (
            "<b>Пользовательское соглашение (Публичная оферта)</b>\n\n"
            "1. Сервис предоставляет услуги по активации и дистанционному обслуживанию устройств Starlink.\n\n"
            "2. Мы не являемся официальным представителем компании Starlink.\n\n"
            "3. Оплата производится на условиях 100% предоплаты. Услуга считается оказанной после активации устройства.\n\n"
            "4. Возврат средств за активированное устройство невозможен по техническим причинам.\n\n"
            "5. Пользователь несет ответственность за правильность указания KIT/SN номеров.\n\n"
            "Полный текст документа доступен на нашем сайте."
        )
        
    keyboard = [
        [InlineKeyboardButton("Открыть на сайте", url=LEGAL_URL)],
        [InlineKeyboardButton("В начало", callback_data="back_start")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Starlink Mini V5", callback_data="svc_mini")],
        [InlineKeyboardButton("Starlink V3 / V4", callback_data="svc_v3")],
        [InlineKeyboardButton("Консультация", callback_data="svc_consult")],
        [InlineKeyboardButton("В начало", callback_data="back_start")],
    ]
    await query.edit_message_text(
        "Выберите интересующую услугу:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_service_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data
    svc = SERVICES.get(key)
    if not svc:
        return

    if key == "svc_consult":
        keyboard = [
            [InlineKeyboardButton("Написать в Telegram", url="https://t.me/svoi_activ")],
            [InlineKeyboardButton("Назад к услугам", callback_data="services")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("Узнать цену / оплатить", callback_data=f"pay_{key}")],
            [InlineKeyboardButton("Назад к услугам", callback_data="services")],
        ]

    await query.edit_message_text(
        f"<b>{svc['title']}</b>\n\n{svc['desc']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def handle_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.replace("pay_", "")
    svc = SERVICES.get(key)
    if not svc:
        return

    user = query.from_user
    product = svc["title"]

    admin_text = (
        f"<b>Новая заявка на оплату</b>\n\n"
        f"Пользователь: {user.full_name}\n"
        f"Username: @{user.username if user.username else '—'}\n"
        f"ID: {user.id}\n"
        f"Товар: {product}"
    )
    
    # Отправляем только на один конкретный ID
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Не удалось уведомить админа {ADMIN_CHAT_ID}: {e}")

    pay_url = None
    if svc.get("price"):
        pay_url = await create_payment(svc["price"], f"Оплата: {product}")

    if pay_url:
        text = (
            f"Ссылка на оплату {product}:\n{pay_url}\n\n"
            "После оплаты менеджер свяжется с вами."
        )
        keyboard = [
            [InlineKeyboardButton("Перейти к оплате", url=pay_url)],
            [InlineKeyboardButton("Назад к услугам", callback_data="services")]
        ]
    else:
        text = (
            f"Заявка на <b>{product}</b> принята.\n\n"
            "Менеджер свяжется с вами в ближайшее время и пришлёт ссылку на оплату."
        )
        keyboard = [[InlineKeyboardButton("Назад к услугам", callback_data="services")]]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "<b>Свяжитесь с нами:</b>\n\n"
        "Телефон: 8-980-475-95-51\n"
        "Email: svoilink@mail.ru\n"
        "Telegram: @svoi_activ",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Назад к услугам", callback_data="services")]]
        ),
        parse_mode="HTML"
    )


async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)


# ========== ЗАПУСК ==========
def main():
    if not BOT_TOKEN:
        logger.error("ОШИБКА: Не задан BOT_TOKEN в переменных окружения!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_services, pattern="^services$"))
    app.add_handler(CallbackQueryHandler(show_service_detail, pattern="^svc_"))
    app.add_handler(CallbackQueryHandler(handle_pay, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(show_legal, pattern="^legal_")) 
    app.add_handler(CallbackQueryHandler(back_start, pattern="^back_start$"))
    
    logger.info("Бот СВОЙLINK запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()