import asyncio
import logging
import os
import uuid as uuidlib

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CopyTextButton,
    CallbackQuery,
)

from bot.api_client import ApiClient, ApiError
from bot.rate_limit import ActionRateLimiter
from bot.states import OwnerStates, SenderStates


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tg-bot")


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000"
)


rate_limiter = ActionRateLimiter(
    max_requests=5,
    window_seconds=60
)

api = ApiClient(API_BASE_URL)

router = Router()

bot_username: str | None = None


# =====================================
# HELPERS
# =====================================

def _parse_command_args(text: str) -> list[str]:
    return text.strip().split()


def _is_valid_uuid(value: str) -> bool:
    try:
        uuidlib.UUID(value)
        return True

    except Exception:
        return False


async def _get_bot_username_cached(
    bot: Bot
) -> str:
    global bot_username

    if bot_username:
        return bot_username

    me = await bot.get_me()

    bot_username = me.username or ""

    if not bot_username:
        raise RuntimeError(
            "Bot username is empty"
        )

    return bot_username


# =====================================
# START
# =====================================

@router.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext
):
    args = _parse_command_args(
        message.text or ""
    )

    payload = (
        args[1]
        if len(args) >= 2
        else None
    )

    # обычный /start
    if not payload:

        await state.clear()

        await message.answer(
            "🤖 <b>Бот анонимных отзывов</b>\n\n"
            "📦 Создать бокс: /newbox\n"
            "📖 Помощь: /help"
        )

        return

    # deep link
    if not _is_valid_uuid(payload):

        await message.answer(
            "❌ Ссылка некорректна."
        )

        return

    # режим отправки отзыва
    await state.set_state(
        SenderStates.awaiting_feedback_text
    )

    await state.update_data(
        box_uuid=payload
    )

    await message.answer(
        "✍️ Напишите анонимный отзыв."
    )


# =====================================
# HELP
# =====================================

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📖 <b>Команды</b>\n\n"

        "/start — меню\n"
        "/newbox — создать бокс\n"
        "/reviews <uuid> <token>\n"
        "/reply <feedback_id> <token>\n"
        "/cancel — отмена"
    )


# =====================================
# CANCEL
# =====================================

@router.message(Command("cancel"))
async def cancel(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "❌ Действие отменено."
    )


# =====================================
# NEW BOX
# =====================================

@router.message(Command("newbox"))
async def newbox(
    message: Message,
    state: FSMContext
):
    user_id = message.from_user.id

    if not rate_limiter.allow(
        user_id,
        "newbox"
    ):
        await message.answer(
            "⏳ Слишком часто."
        )

        return

    try:
        payload = await api.create_box()

    except ApiError as e:

        await message.answer(
            f"❌ Ошибка:\n"
            f"{e.status_code} {e.detail}"
        )

        return

    username = await _get_bot_username_cached(
        message.bot
    )

    box_uuid = payload["uuid"]
    owner_token = payload["owner_token"]

    link = (
        f"https://t.me/{username}"
        f"?start={box_uuid}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Скопировать UUID",
                    copy_text=CopyTextButton(
                        text=box_uuid
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Скопировать токен",
                    copy_text=CopyTextButton(
                        text=owner_token
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔗 Открыть ссылку",
                    url=link
                )
            ]
        ]
    )

    await message.answer(
        "✅ <b>Бокс создан!</b>\n\n"

        f"🔑 UUID:\n"
        f"<code>{box_uuid}</code>\n\n"

        f"🛡️ Токен:\n"
        f"<code>{owner_token}</code>\n\n"

        f"🔗 Ссылка:\n"
        f"{link}",

        reply_markup=keyboard
    )

    await state.clear()


# =====================================
# REVIEWS
# =====================================

@router.message(Command("reviews"))
async def reviews(
    message: Message,
    state: FSMContext
):
    args = _parse_command_args(
        message.text or ""
    )

    if len(args) != 3:

        await message.answer(
            "/reviews <uuid> <token>"
        )

        return

    _, box_uuid, token = args

    if not _is_valid_uuid(box_uuid):

        await message.answer(
            "❌ UUID некорректен."
        )

        return

    try:
        payload = await api.get_box_feedbacks(
            box_uuid,
            token
        )

    except ApiError as e:

        if e.status_code == 403:

            await message.answer(
                "❌ Неверный токен."
            )

        elif e.status_code == 404:

            await message.answer(
                "❌ Бокс не найден."
            )

        else:

            await message.answer(
                f"❌ Ошибка:\n"
                f"{e.status_code} {e.detail}"
            )

        return

    feedbacks = payload.get(
        "feedbacks"
    ) or []

    if not feedbacks:

        await message.answer(
            "📭 Отзывов пока нет."
        )

        return

    # сохраняем token
    await state.update_data(
        owner_token=token
    )

    for fb in feedbacks:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💬 Ответить",
                        callback_data=(
                            f"reply:{fb['id']}"
                        )
                    )
                ]
            ]
        )

        await message.answer(
            f"📝 <b>Отзыв #{fb['id']}</b>\n\n"
            f"{fb['text']}\n\n"
            f"📅 {fb['created_at']}",

            reply_markup=keyboard
        )


# =====================================
# CALLBACK REPLY
# =====================================

@router.callback_query(
    F.data.startswith("reply:")
)
async def reply_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    feedback_id = int(
        callback.data.split(":")[1]
    )

    data = await state.get_data()

    token = data.get("owner_token")

    if not token:

        await callback.message.answer(
            "❌ Сначала откройте /reviews"
        )

        return

    await state.set_state(
        OwnerStates.awaiting_reply_text
    )

    await state.update_data(
        feedback_id=feedback_id,
        token=token
    )

    await callback.message.answer(
        "✍️ Напишите ответ."
    )

    await callback.answer()


# =====================================
# COMMAND REPLY
# =====================================

@router.message(Command("reply"))
async def reply_start(
    message: Message,
    state: FSMContext
):
    args = _parse_command_args(
        message.text or ""
    )

    if len(args) != 3:

        await message.answer(
            "Использование:\n"
            "/reply <feedback_id> <token>"
        )

        return

    _, feedback_id_str, token = args

    try:
        feedback_id = int(
            feedback_id_str
        )

    except ValueError:

        await message.answer(
            "❌ feedback_id должен "
            "быть числом."
        )

        return

    await state.set_state(
        OwnerStates.awaiting_reply_text
    )

    await state.update_data(
        feedback_id=feedback_id,
        token=token
    )

    await message.answer(
        "✍️ Напишите ответ."
    )


# =====================================
# SEND FEEDBACK
# =====================================

@router.message(
    SenderStates.awaiting_feedback_text,
    F.text & ~F.text.startswith("/")
)
async def sender_feedback(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()

    box_uuid = data.get("box_uuid")

    if not box_uuid:

        await state.clear()

        await message.answer(
            "❌ Состояние потеряно."
        )

        return

    try:
        await api.send_feedback(
            box_uuid=str(box_uuid),
            text=message.text,
            sender_tg_id=(
                message.from_user.id
            )
        )

    except ApiError as e:

        await message.answer(
            f"❌ Ошибка:\n"
            f"{e.status_code} {e.detail}"
        )

        return

    await state.clear()

    await message.answer(
        "✅ Отзыв отправлен."
    )


# =====================================
# OWNER REPLY
# =====================================

@router.message(
    OwnerStates.awaiting_reply_text,
    F.text & ~F.text.startswith("/")
)
async def owner_reply(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()

    feedback_id = data.get(
        "feedback_id"
    )

    token = data.get("token")

    if (
        feedback_id is None
        or not token
    ):
        await state.clear()

        await message.answer(
            "❌ Состояние потеряно."
        )

        return

    try:
        result = await api.send_reply(
            feedback_id=int(feedback_id),
            token=str(token),
            text=message.text
        )

        sender_tg_id = result.get(
            "sender_tg_id"
        )

        # отправка автору
        if sender_tg_id:

            await message.bot.send_message(
                chat_id=sender_tg_id,
                text=(
                    "💬 <b>Вам ответили "
                    "на отзыв</b>\n\n"
                    f"{message.text}"
                )
            )

    except ApiError as e:

        if e.status_code == 403:

            await message.answer(
                "❌ Неверный токен."
            )

        else:

            await message.answer(
                f"❌ Ошибка:\n"
                f"{e.status_code} {e.detail}"
            )

        return

    except Exception as e:

        log.exception(e)

        await message.answer(
            "❌ Не удалось отправить "
            "сообщение пользователю."
        )

        return

    await state.clear()

    await message.answer(
        "✅ Ответ отправлен."
    )


# =====================================
# MAIN
# =====================================

async def main():

    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN "
            "is not set"
        )

    storage = MemoryStorage()

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher(
        storage=storage
    )

    dp.include_router(router)

    try:
        while True:

            try:
                await dp.start_polling(bot)
                break

            except TelegramNetworkError as e:

                log.warning(
                    "Telegram network error: %s",
                    e
                )

                await asyncio.sleep(5)

    finally:
        await storage.close()
        await api.aclose()


if __name__ == "__main__":
    asyncio.run(main())