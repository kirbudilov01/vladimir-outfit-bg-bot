from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, KeyboardButton, Message, ReplyKeyboardMarkup

from .config import Settings
from .db import Store
from .processor import BackgroundComposer


ADMIN_BACKGROUND_MODE: set[int] = set()


def main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text="Статус"), KeyboardButton(text="Помощь")]]
    if is_admin:
        rows.insert(0, [KeyboardButton(text="Задать фон")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, input_field_placeholder="Отправь фото вещи или товара")


def is_admin(message: Message, settings: Settings) -> bool:
    return message.from_user.id in settings.admins


async def register_handlers(dp: Dispatcher, bot: Bot, store: Store, composer: BackgroundComposer, settings: Settings) -> None:
    storage = Path("storage")
    storage.mkdir(exist_ok=True)

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        admin = is_admin(message, settings)
        await message.answer(
            "Outfit Background Bot\n\n"
            "Я переношу вещь или товар с исходной фотографии на постоянный фон.\n\n"
            "Оператор: отправь фото вещи.\n"
            "Админ: нажми Задать фон или используй /set_background.",
            reply_markup=main_keyboard(admin),
        )

    @dp.message(Command("help"))
    @dp.message(F.text.casefold() == "помощь")
    async def help_message(message: Message) -> None:
        await message.answer(
            "Как пользоваться\n\n"
            "1. Админ один раз задает фон.\n"
            "2. Оператор отправляет фото вещи/товара.\n"
            "3. Бот вырезает объект, ставит его на фон и возвращает готовый кадр.\n\n"
            "Лучшие исходники: чистая вещь, хороший свет, без сильных перекрытий руками.",
            reply_markup=main_keyboard(is_admin(message, settings)),
        )

    @dp.message(Command("status"))
    @dp.message(F.text.casefold() == "статус")
    async def status(message: Message) -> None:
        background = Path(settings.background_path)
        state = "задан" if background.exists() else "не задан"
        await message.answer(
            "Статус\n\n"
            f"Фон: {state}\n"
            f"Файл фона: {settings.background_path}\n"
            f"Ширина размещения: {settings.placement_width_ratio:.2f}\n"
            f"Высота размещения: {settings.placement_height_ratio:.2f}\n"
            f"Нижний отступ: {settings.placement_bottom_margin_ratio:.2f}",
            reply_markup=main_keyboard(is_admin(message, settings)),
        )

    @dp.message(Command("cancel"))
    async def cancel(message: Message) -> None:
        ADMIN_BACKGROUND_MODE.discard(message.from_user.id)
        await message.answer("Режим ожидания фона отменен.", reply_markup=main_keyboard(is_admin(message, settings)))

    @dp.message(Command("set_background"))
    @dp.message(F.text.casefold() == "задать фон")
    async def set_background(message: Message) -> None:
        if not is_admin(message, settings):
            await message.answer("Команда только для администратора.")
            return
        ADMIN_BACKGROUND_MODE.add(message.from_user.id)
        await message.answer("Отправь картинку фона одним фото. Отмена: /cancel")

    @dp.message(F.photo)
    async def photo(message: Message) -> None:
        admin = is_admin(message, settings)
        if message.from_user.id in ADMIN_BACKGROUND_MODE:
            bg_path = Path(settings.background_path)
            bg_path.parent.mkdir(parents=True, exist_ok=True)
            await bot.download(message.photo[-1], destination=bg_path)
            ADMIN_BACKGROUND_MODE.discard(message.from_user.id)
            await message.answer("Фон сохранен. Теперь можно отправлять исходники для переноса.", reply_markup=main_keyboard(admin))
            return

        background = Path(settings.background_path)
        if not background.exists():
            await message.answer("Фон еще не задан. Администратор должен нажать Задать фон или выполнить /set_background.")
            return

        token = uuid4().hex
        input_path = storage / f"{message.from_user.id}_{token}_input.jpg"
        output_path = storage / f"{message.from_user.id}_{token}_output.jpg"
        await bot.download(message.photo[-1], destination=input_path)
        progress = await message.answer("Фото принято. Вырезаю объект и переношу на постоянный фон.")
        try:
            await asyncio.to_thread(composer.compose, input_path, output_path)
        except Exception as exc:
            await progress.edit_text(
                "Не получилось обработать фото. Попробуй исходник с более чистым объектом и контрастным фоном.\n"
                f"Техническая причина: {type(exc).__name__}"
            )
            return
        store.save_job(message.from_user.id, str(input_path), str(output_path))
        result = BufferedInputFile(output_path.read_bytes(), filename="outfit-background-result.jpg")
        await progress.edit_text("Готово. Отправляю результат.")
        await message.answer_photo(photo=result, caption="Готово. Можно отправить следующий исходник.", reply_markup=main_keyboard(admin))

    @dp.message()
    async def fallback(message: Message) -> None:
        await message.answer(
            "Отправь фото вещи/товара. Админ может сменить фон кнопкой Задать фон.",
            reply_markup=main_keyboard(is_admin(message, settings)),
        )
