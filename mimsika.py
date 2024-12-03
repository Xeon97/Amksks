# -*- coding: utf-8 -*-
# meta developer: @YourTelegramUsername
# meta banner: https://via.placeholder.com/600x200.png?text=RPG+Game+Module
# meta description: Простая RPG игра для Hikka Userbot.
# meta license: MIT

import random
from .. import loader, utils
from hikka import events

players = {}
items = {
    "sword": {"price": 50, "power": 10},
    "shield": {"price": 30, "defense": 5},
}

@loader.tds
class RPGGameMod(loader.Module):
    """RPG Game Module"""

    strings = {"name": "RPGGame"}

    async def profilecmd(self, message):
        """Показать ваш профиль игрока"""
        user_id = utils.get_chat_id(message)
        if user_id not in players:
            players[user_id] = {"level": 1, "exp": 0, "gold": 100, "items": []}
        profile = players[user_id]
        response = (
            f"🎮 Профиль игрока:\n"
            f"👤 Игрок: {utils.escape_html(message.sender.first_name)}\n"
            f"⭐ Уровень: {profile['level']}\n"
            f"⚡ Опыт: {profile['exp']}\n"
            f"💰 Золото: {profile['gold']}\n"
            f"🎒 Предметы: {', '.join(profile['items']) or 'нет'}"
        )
        await utils.answer(message, response)

    async def startgamecmd(self, message):
        """Начать игру для всех участников чата"""
        chat_id = message.chat.id
        await utils.answer(message, "🎮 Игра начинается! Удачи всем игрокам!")

        # Начинаем игру для всех пользователей в чате
        async for user in self._client.iter_participants(chat_id):
            if user.id not in players:
                players[user.id] = {"level": 1, "exp": 0, "gold": 100, "items": []}
            profile = players[user.id]
            # Приветственное сообщение для каждого игрока
            await utils.answer(message, f"🎮 Игрок {utils.escape_html(user.first_name)} подключился к игре! Начнем с уровня 1.")

    async def questcmd(self, message):
        """Начать новый квест для всех игроков"""
        question = random.choice([
            {"q": "Я без рук и без ног, но всех обнимаю. Что я?", "a": "кровать"},
            {"q": "Что всегда идёт, но никогда не приходит?", "a": "время"},
        ])
        await utils.answer(message, f"🎲 Новый квест!\nЗагадка: {question['q']}")

        # Обработчик для ответа на загадку от всех игроков
        @self._client.on(events.NewMessage(incoming=True))
        async def check_answer(event):
            user_id = event.sender_id
            if event.text.lower() == question['a']:
                winner = event.sender.first_name
                players[user_id]["gold"] += 10  # Награда за правильный ответ
                await utils.answer(event, f"🎉 {utils.escape_html(winner)} правильно ответил на загадку!")
                self._client.remove_event_handler(check_answer)  # Удаляем обработчик после ответа

    async def shopcmd(self, message):
        """Открыть магазин"""
        shop_items = "\n".join([f"{name} - {data['price']} золота" for name, data in items.items()])
        await utils.answer(message, f"🛒 Магазин:\n{shop_items}\n\nДля покупки используйте .buy <предмет>")

    async def buycmd(self, message):
        """Купить предмет из магазина для себя: .buy <item>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ Укажите предмет для покупки!")
            return

        item_name = args.lower()
        user_id = utils.get_chat_id(message)
        if item_name not in items:
            await utils.answer(message, "❌ Предмет не найден!")
            return

        if players[user_id]["gold"] >= items[item_name]["price"]:
            players[user_id]["gold"] -= items[item_name]["price"]
            players[user_id]["items"].append(item_name)
            await utils.answer(message, f"🎉 Вы купили {item_name}!")
        else:
            await utils.answer(message, "❌ У вас недостаточно золота!")