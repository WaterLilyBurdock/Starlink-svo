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
            "<b>1. Термины и определения</b>\n"
            "1.1. <b>Оферта</b> – настоящее Пользовательское соглашение.\n"
            "1.2. <b>Сервис</b> – Telegram-бот @starlink_zakaz_bot, принадлежащий Исполнителю и предназначенный для оказания услуг.\n"
            "1.3. <b>Пользователь</b> – любое физическое лицо, акцептовавшее (принявшее) настоящую Оферту.\n"
            "1.4. <b>Услуга</b> – активация и последующее дистанционное обслуживание устройств Starlink.\n"
            "1.5. <b>Акцепт Оферты</b> – совершение Пользователем оплаты Товара через Сервис. Акцепт означает полное и безоговорочное согласие Пользователя со всеми условиями настоящей Оферты.\n\n"
            "<b>2. Предмет Оферты</b>\n"
            "2.1. Исполнитель обязуется оказать услугу (активировать устройство с последующим дистанционным сопровождением) Пользователю, а Пользователь обязуется оплатить Услугу в соответствии с условиями настоящей Оферты.\n"
            "2.2. Сервис «starlink_zakaz_bot» является независимой площадкой и не является аффилированным лицом или официальным представителем компании Starlink.\n\n"
            "<b>3. Порядок оплаты и предоставления Товара</b>\n"
            "3.1. Стоимость Услуг и их наименования определяются Пользователем в интерфейсе Сервиса (@starlink_zakaz_bot) перед оплатой.\n"
            "3.2. Оплата производится на условиях 100% предоплаты через платежную систему MulenPay (СБП).\n"
            "3.3. Оказание Услуг Пользователю производится в среднем в течение 1-2 часов (активация, продление подписки устройств Starlink), в исключительных случаях, по независящим от Исполнителя условиям время оказания Услуги может быть увеличено, с уведомлением об этом Пользователя.\n"
            "3.4. <b>Пользователь несет полную ответственность за корректность указания номера устройства для активации и последующего продления (KIT/SN номера).</b> В случае предоставления неверных данных и активации, либо продления другого устройства, услуга считается оказанной надлежащим образом, и возврат средств не производится.\n\n"
            "<b>4. Условия возврата и отмены</b>\n"
            "4.1. <b>Возврат Товара надлежащего качества невозможен.</b> После успешной активации и продления устройства Starlink, услуга считается оказанной в полном объеме, и возврат денежных средств не производится. Это обусловлено техническими особенностями и политикой платформы Starlink.\n\n"
            "<b>5. Права и обязанности сторон</b>\n"
            "5.1. <b>Исполнитель обязан:</b>\n"
            "• Предоставить Услугу в соответствии с условиями Оферты.\n"
            "• Произвести активацию устройства и оказывать последующую поддержку устройства Пользователя.\n"
            "• Не разглашать данные Пользователя, за исключением случаев, предусмотренных законодательством и Политикой обработки персональных данных.\n"
            "5.2. <b>Пользователь обязан:</b>\n"
            "• Внимательно ознакомиться с условиями Оферты.\n"
            "• Предоставлять корректные данные для активации устройства Starlink.\n"
            "• Использовать устройство Starlink в соответствии с правилами и политиками платформы Starlink.\n\n"
            "<b>6. Ответственность и форс-мажор</b>\n"
            "6.1. Исполнитель не несет ответственности за дальнейшее использование устройства Пользователем, включая его блокировку, уничтожение или иные действия со стороны платформы Starlink.\n"
            "6.2. Стороны освобождаются от ответственности за частичное или полное неисполнение обязательств по настоящей Оферте, если это неисполнение явилось следствием обстоятельств непреодолимой силы (форс-мажор).\n"
            "6.3. К форс-мажорным обстоятельствам, помимо прочего, относятся: глобальные сбои в работе сети Интернет, глобальные сбои в работе платформы Starlink, решения органов государственной власти, блокировки сервисов на территории страны Пользователя или Исполнителя.\n\n"
            "<b>7. Разрешение споров</b>\n"
            "7.1. Все споры и разногласия решаются путем переговоров. Официальный канал для связи со службой поддержки указан в интерфейсе Сервиса (@starlink_zakaz_bot). На момент составления Оферты это аккаунт @Starlink_aktiv.\n"
            "7.2. В случае невозможности разрешить спор путем переговоров, он подлежит рассмотрению в суде в соответствии с действующим законодательством.\n\n"
            "<b>8. Срок действия Оферты</b>\n"
            "8.1. Настоящая Оферта вступает в силу с момента ее публикации и действует до момента ее отзыва Исполнителем.\n"
            "8.2. Исполнитель оставляет за собой право вносить изменения в Оферту, которые вступают в силу с момента публикации новой версии."
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