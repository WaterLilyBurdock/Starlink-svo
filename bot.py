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

LEGAL_DOCS = {
    "legal_privacy": {
        "file": "Политика-Конф.docx",
        "filename": "Политика конфиденциальности.docx",
        "caption": "<b>Политика конфиденциальности</b>",
        "read_callback": "read_privacy",
    },
    "legal_terms": {
        "file": "Пользовательское-Согласшение.docx",
        "filename": "Пользовательское соглашение.docx",
        "caption": "<b>Пользовательское соглашение (Публичная оферта)</b>",
        "read_callback": "read_terms",
    },
}

LEGAL_TEXTS = {
    "read_privacy": (
        "<b>Политика конфиденциальности</b>\n\n"
        "<b>1. ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ</b>\n"
        "<b>Персональные данные</b> - любая информация, относящаяся к определенному или определяемому на основании такой информации физическому лицу (субъекту персональных данных).\n"
        "<b>Обработка персональных данных</b> – любое действие (операция) или совокупность действий (операций), совершаемых с использованием средств автоматизации или без использования таких средств с персональными данными, включая сбор, запись, систематизацию, накопление, хранение, уточнение (обновление, изменение), извлечение, использование, передачу (распространение, предоставление, доступ), обезличивание, блокирование, удаление, уничтожение персональных данных.\n"
        "<b>Конфиденциальность персональных данных</b> - обязательное для соблюдения допущенными к обработке персональных данных пользователей требование надлежаще соблюдать правила их обработки, хранения, не допускать их распространения без согласия субъекта или иного законного основания.\n"
        "<b>Использование персональных данных</b> - действия (операции) с персональными данными, направленные на идентификацию Пользователя с целью предоставления доступа к сервису и получение подтверждения достоверности указанной Пользователем информации.\n"
        "<b>Информация</b> - сведения (сообщения, данные) независимо от формы их представления.\n"
        "<b>Общедоступные персональные данные</b> - персональные данные, доступ неограниченного круга лиц к которым предоставлен с согласия субъекта или на которые в соответствии с федеральными законами не распространяется требование соблюдения конфиденциальности.\n"
        "<b>Оператор</b> - Компания, осуществляющая обработку персональных данных пользователей в целях предоставления последним авторизованного доступа ко всем сервисам, а также определяющая цели обработки персональных данных, состав персональных данных, действия (операции), совершаемые с персональными данными, порядок хранения и уничтожения персональных данных пользователей.\n"
        "<b>Пользователь</b> - посетитель сервиса.\n"
        "<b>Распространение персональных данных</b> – любые действия, направленные на раскрытие персональных данных неопределенному кругу лиц (передача персональных данных) или на ознакомление с персональными данными неограниченного круга лиц.\n"
        "<b>Уничтожение персональных данных</b> – любые действия, в результате которых персональные данные уничтожаются безвозвратно с невозможностью дальнейшего восстановления содержания персональных данных в информационной системе персональных данных.\n\n"
        "<b>2. ПРАВА И ОБЯЗАННОСТИ</b>\n"
        "2.1. Оператор имеет право:\n"
        "2.1.1. Получать от субъекта персональных данных достоверные информацию и/или документы, содержащие персональные данные;\n"
        "2.1.2. В случае отзыва субъектом персональных данных согласия на обработку персональных данных Оператор вправе продолжить обработку персональных данных без согласия субъекта персональных данных при наличии оснований, указанных в Законе о персональных данных;\n"
        "2.1.3. Самостоятельно определять состав и перечень мер, необходимых и достаточных для обеспечения выполнения обязанностей, предусмотренных Законом о персональных данных и принятыми в соответствии с ним нормативными правовыми актами.\n"
        "2.2. Оператор обязан:\n"
        "2.2.1. Организовывать обработку персональных данных в порядке, установленном действующим законодательством РФ;\n"
        "2.2.2. Отвечать на обращения и запросы субъектов персональных данных и их законных представителей в соответствии с требованиями Закона о персональных данных;\n"
        "2.2.3. Прекратить передачу (распространение, предоставление, доступ) персональных данных, прекратить обработку и уничтожить персональные данные в порядке и случаях, предусмотренных Законом о персональных данных.\n"
        "2.3. Субъекты персональных данных имеют право:\n"
        "2.3.1. Получать информацию, касающуюся обработки персональных данных субъекта, за исключением случаев, предусмотренных федеральными законами.\n"
        "2.3.2. Требовать от оператора уточнения его персональных данных, их блокирования или уничтожения в случае, если персональные данные являются неполными, устаревшими, неточными, незаконно полученными или не являются необходимыми для заявленной цели обработки.\n"
        "2.4. Субъекты персональных данных обязаны:\n"
        "2.4.1. Предоставлять Оператору достоверные данные о себе;\n"
        "2.4.2. Сообщать Оператору об уточнении (обновлении, изменении) своих персональных данных.\n\n"
        "<b>3. ПРИНЦИПЫ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ</b>\n"
        "3.1. Обработка персональных данных осуществляется на законной и справедливой основе.\n"
        "3.2. Обработка персональных данных ограничивается достижением конкретных, заранее определенных и законных целей. Не допускается обработка персональных данных, несовместимая с целями сбора персональных данных.\n"
        "3.3. Не допускается объединение баз данных, содержащих персональные данные, обработка которых осуществляется в целях, несовместимых между собой.\n"
        "3.4. Обработке подлежат только персональные данные, которые отвечают целям их обработки.\n"
        "3.5. Содержание и объем обрабатываемых персональных данных соответствуют заявленным целям обработки. Не допускается избыточность обрабатываемых персональных данных по отношению к заявленным целям их обработки.\n"
        "3.6. При обработке персональных данных обеспечивается точность персональных данных, их достаточность, а в необходимых случаях и актуальность по отношению к целям обработки персональных данных. Оператор принимает необходимые меры и/или обеспечивает их принятие по удалению или уточнению неполных или неточных данных.\n"
        "3.7. Хранение персональных данных осуществляется в форме, позволяющей определить субъекта персональных данных, не дольше, чем этого требуют цели обработки персональных данных, если срок хранения персональных данных не установлен федеральным законом, договором, стороной которого является субъект персональных данных.\n\n"
        "<b>4. ЦЕЛИ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ</b>\n"
        "4.1. Цель обработки персональных данных Пользователя:\n"
        "4.1.1. Информирование Пользователя;\n"
        "4.1.2. Предоставление доступа Пользователю к сервису;\n"
        "4.2. Оператор имеет право направлять Пользователю уведомления о новых продуктах и услугах, специальных предложениях и различных событиях. Пользователь всегда может отказаться от получения информационных сообщений, направив Оператору письмо на Адрес электронной почты.\n\n"
        "<b>5. КОНФИДЕНЦИАЛЬНОСТЬ ПЕРСОНАЛЬНЫХ ДАННЫХ</b>\n"
        "5.1. Оператор и иные лица, получившие доступ к персональным данным, обязаны не раскрывать третьим лицам и не распространять персональные данные без согласия субъекта персональных данных, если иное не предусмотрено федеральным законом.\n\n"
        "<b>6. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</b>\n"
        "6.1. Пользователь может получить любые разъяснения по интересующим вопросам, касающимся обработки его персональных данных, обратившись к Оператору с помощью электронной почты.\n"
        "6.2. В данном документе будут отражены любые изменения политики обработки персональных данных Оператором. Политика действует бессрочно до замены ее новой версией."
    ),
    "read_terms": (
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
    ),
}


async def send_long_html(message, text: str, reply_markup=None, chunk_size: int = 4000):
    """Отправляет длинный HTML-текст частями в пределах лимита Telegram (4096 символов)."""
    chunks = []
    current = ""
    for para in text.split("\n\n"):
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
                current = ""
            if len(para) <= chunk_size:
                current = para
            else:
                for line in para.split("\n"):
                    line_cand = f"{current}\n{line}" if current else line
                    if len(line_cand) <= chunk_size:
                        current = line_cand
                    else:
                        if current:
                            chunks.append(current)
                        current = line
    if current:
        chunks.append(current)

    for idx, chunk in enumerate(chunks):
        markup = reply_markup if idx == len(chunks) - 1 else None
        await message.reply_text(chunk, reply_markup=markup, parse_mode="HTML")


async def show_legal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    doc_meta = LEGAL_DOCS.get(query.data)
    if not doc_meta:
        return

    read_cb = doc_meta["read_callback"]
    keyboard = [
        [InlineKeyboardButton("Читать текстом в Telegram", callback_data=read_cb)],
        [InlineKeyboardButton("Открыть на сайте", url=LEGAL_URL)],
        [InlineKeyboardButton("В начало", callback_data="back_start")],
    ]

    doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), doc_meta["file"])
    if os.path.isfile(doc_path):
        with open(doc_path, "rb") as f:
            await query.message.reply_document(
                document=f,
                filename=doc_meta["filename"],
                caption=doc_meta["caption"],
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )
        return

    fallback_keyboard = [
        [InlineKeyboardButton("Открыть на сайте", url=LEGAL_URL)],
        [InlineKeyboardButton("В начало", callback_data="back_start")],
    ]
    await send_long_html(
        query.message,
        LEGAL_TEXTS[read_cb],
        reply_markup=InlineKeyboardMarkup(fallback_keyboard),
    )


async def show_legal_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = LEGAL_TEXTS.get(query.data)
    if not text:
        return

    keyboard = [
        [InlineKeyboardButton("Открыть на сайте", url=LEGAL_URL)],
        [InlineKeyboardButton("В начало", callback_data="back_start")],
    ]
    await send_long_html(query.message, text, reply_markup=InlineKeyboardMarkup(keyboard))


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
    app.add_handler(CallbackQueryHandler(show_legal_text, pattern="^read_"))
    app.add_handler(CallbackQueryHandler(back_start, pattern="^back_start$"))
    
    logger.info("Бот СВОЙLINK запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()