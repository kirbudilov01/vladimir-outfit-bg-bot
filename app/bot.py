from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from .config import Settings
from .db import Store
from .processor import BackgroundComposer


ADMIN_BACKGROUND_MODE: set[int] = set()


async def register_handlers(dp: Dispatcher, bot: Bot, store: Store, composer: BackgroundComposer, settings: Settings) -> None:
    storage = Path("storage")
    storage.mkdir(exist_ok=True)

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(
            "Бот переносит вещь/товар с исходной фотографии на постоянный фон.\n\n"
            "Админ: /set_background, затем отправь фон.\n"
            "Оператор: отправь фото вещи, бот вернёт готовый кадр."
        )

    @dp.message(Command("set_background"))
    async def set_background(message: Message) -> None:
        if message.from_user.id not in settings.admins:
            await message.answer("Команда только для администратора.")
            return
        ADMIN_BACKGROUND_MODE.add(message.from_user.id)
        await message.answer("Отправь картинку фона одним фото.")

    @dp.message(F.photo)
    async def photo(message: Message) -> None:
        if message.from_user.id in ADMIN_BACKGROUND_MODE:
            bg_path = Path(settings.background_path)
            bg_path.parent.mkdir(parents=True, exist_ok=True)
            await bot.download(message.photo[-1], destination=bg_path)
            ADMIN_BACKGROUND_MODE.discard(message.from_user.id)
            await message.answer("Фон сохранён. Теперь можно отправлять исходники для переноса.")
            return

        token = uuid4().hex
        input_path = storage / f"{message.from_user.id}_{token}_input.jpg"
        output_path = storage / f"{message.from_user.id}_{token}_output.jpg"
        await bot.download(message.photo[-1], destination=input_path)
        await message.answer("Фото принял. Вырезаю объект и переношу на постоянный фон.")
        try:
            composer.compose(input_path, output_path)
        except FileNotFoundError:
            await message.answer("Фон ещё не задан. Администратор должен выполнить /set_background.")
            return
        store.save_job(message.from_user.id, str(input_path), str(output_path))
        result = BufferedInputFile(output_path.read_bytes(), filename="outfit-background-result.jpg")
        await message.answer_photo(photo=result, caption="Готово.")

    @dp.message()
    async def fallback(message: Message) -> None:
        await message.answer("Отправь фото вещи/товара. Админ может сменить фон через /set_background.")
