from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import states
from logger import LoggingMiddleware
import utils
from config import WHEATHER_API_KEY

router = Router()
router.message.middleware(LoggingMiddleware())
# router.callback_query.middleware(LoggingMiddleware())

users = {}

async def update_user(id):
    if id not in users:
        users[id] = {
            "weight": 0,
            "height": 0,
            "age": 0,
            "active_time": 0,
            "city": "",
            "water_goal": 0,
            "calorie_goal": 0,
            "logged_water": 0,
            "logged_calories": 0,
            "burned_calories": 0,

            "wait_calories": 0
        }


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Это проект 2 по курсу \"Прикладной Python\" студента @maleksjuk")
    user_id = message.from_user.id
    await update_user(user_id)

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("""
Доступные команды:
/start
/help
/cancel

/set_profile
/user_info

/log_water
/log_food
/log_workout
/check_progress
""")


@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await update_user(message.from_user.id)
    await message.answer("Настроим ваш профиль.\nВведите ваш вес (в кг)")
    await state.set_state(states.Profile.weight)

@router.message(states.Profile.weight)
async def set_profile_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
    except:
        await message.reply("Ошибка чтения веса. Повторите ввод или отмените настройку /cancel")
        return
    user = message.from_user.id
    users[user]["weight"] = weight
    await message.answer(f"Ваш вес (в кг): {weight}.\nВведите ваш рост (в см)")
    await state.set_state(states.Profile.height)

@router.message(states.Profile.height)
async def set_profile_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        await state.update_data(height=height)
    except:
        await message.reply("Ошибка чтения роста. Повторите ввод или отмените настройку /cancel")
        return
    user = message.from_user.id
    users[user]["height"] = height
    await message.answer(f"Ваш рост (в см): {height}.\nВведите ваш возраст")
    await state.set_state(states.Profile.age)

@router.message(states.Profile.age)
async def set_profile_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
    except:
        await message.reply("Ошибка чтения возраста. Повторите ввод или отмените настройку /cancel")
        return
    user = message.from_user.id
    users[user]["age"] = age
    await message.answer(f"Ваш возраст: {age}.\nСколько минут активности у вас в день?")
    await state.set_state(states.Profile.active_time)

@router.message(states.Profile.active_time)
async def set_profile_active_time(message: Message, state: FSMContext):
    try:
        active_time = int(message.text)
        await state.update_data(active_time=active_time)
    except:
        await message.reply("Ошибка чтения времени активности. Повторите ввод или отмените настройку /cancel")
        return
    user = message.from_user.id
    users[user]["active_time"] = active_time
    await message.answer(f"Ваше время активности в день: {active_time}.\nВ каком городе вы находитесь?")
    await state.set_state(states.Profile.city)

@router.message(states.Profile.city)
async def set_profile_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    user = message.from_user.id
    users[user]["city"] = city
    await message.answer(f"Ваш город: {city}.\nНастройка завершена!")
    await state.clear()
    await update_goals(user)

async def update_goals(user_id):
    weight = users[user_id]["weight"]
    height = users[user_id]["height"]
    age = users[user_id]["age"]
    active_time = users[user_id]["active_time"]
    city = users[user_id]["city"]

    users[user_id]["water_goal"] = weight * 30 + 500 * active_time // 30 + (500 if await city_temperature(city) > 25 else 0)

    users[user_id]["calorie_goal"] = 10 * weight + 6.25 * height - 5 * age + 300

async def city_temperature(city: str):
    temp = await utils.get_temperature(city, WHEATHER_API_KEY)
    # print(temp['data']['main']['temp'])
    if not temp:
        return 0
    return temp['main']['temp']

@router.message(Command("user_info"))
async def get_user_info(message: Message):
    user = message.from_user.id
    data = users[user]
    await message.answer(f"""Информация о пользователе

Рост: {data["height"]} см
Вес: {data["weight"]} кг
Возраст: {data["age"]}
Время активности: {data["active_time"]} мин
Город: {data["city"]}""")


@router.message(Command("log_water"))
async def cmd_log_water(message: Message) -> None:
    user_id = message.from_user.id
    args = message.text.strip().split()
    if len(args) != 2:
        await message.answer("Введите количество выпитой воды в формате \"/log_water <количество>\"")
    else:
        try:
            water_count = int(args[1])
        except:
            await message.answer("Ошибка чтения количества воды")
            return
        users[user_id]["logged_water"] += water_count
        await message.answer(f"Норма воды: {users[user_id]["water_goal"]} мл\n"
                             f"Выпито воды: {users[user_id]["logged_water"]} мл\n"
                             f"Осталось до выполнения нормы: {users[user_id]["water_goal"] - users[user_id]["logged_water"]} мл")


@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    user_id = message.from_user.id
    args = message.text.strip().split()
    if len(args) == 1:
        await message.answer("Введите название продукта в формате \"/log_food <название продукта>\"")
        # await state.set_state(states.FoodLogging.food)
        return
    
    calories = 0
    food_name = " ".join(args[1:])
    data = await utils.get_product_calories(food_name)
    if data:
        food_name = data["name"]
        calories = data["calories"]
    users[user_id]["wait_calories"] = calories // 100
    await message.answer(f"{food_name.capitalize()} - {calories} ккал на 100 г. Сколько грамм вы съели?")
    await state.set_state(states.Calories.count)


@router.message(states.Calories.count)
async def cmd_log_food_count(message: Message, state: FSMContext):
    await state.clear()
    try:
        count = float(message.text)
    except:
        await message.reply("Ошибка чтения количества продукта")
        return
    user_id = message.from_user.id
    calories = users[user_id]["wait_calories"]
    eated_calories = calories * count
    users[user_id]["logged_calories"] += eated_calories
    await message.answer(f"Записано {eated_calories:.2f} ккал")


@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message):
    user_id = message.from_user.id
    args = message.text.strip().split()
    if len(args) < 3:
        await message.answer("Введите данные о тренировке в формате \"/log_workout <тип тренировки> <время в минутах>\"")
    else:
        workout_data = " ".join(args[1:-1])
        try:
            workout_time = int(args[-1])
        except:
            await message.answer("Ошибка чтения времени тренировки")
            return
        
        #data API
        burn_calories = 0

        users[user_id]["burned_calories"] += burn_calories
        await message.answer(f"Тренировка \"{workout_data}\" в течение {workout_time} мин. Потрачено калорий: {burn_calories} ккал.\n"
                             f"Дополнительно выпейте {workout_time // 30} мл воды.")


@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    user_id = message.from_user.id
    water_target = users[user_id]["water_goal"]
    water_logged = users[user_id]["logged_water"]
    calories_target = users[user_id]["calorie_goal"]
    calories_logged = users[user_id]["logged_calories"]
    calories_burned = users[user_id]["burned_calories"]

    text = "Прогресс:\n"
    text += "Вода:\n"
    text += f"- цель: {water_target} мл\n"
    text += f"- выпито: {water_logged} мл\n"
    text += f"- осталось: {water_target - water_logged} мл\n" if water_target - water_logged > 0 else ""

    text += "\nКалории:\n"
    text += f"- цель: {calories_target} ккал\n"
    text += f"- съедено: {calories_logged} ккал\n"
    text += f"- сожжено: {calories_burned} ккал\n"
    text += f"- баланс: {calories_logged - calories_burned} ккал"

    await message.answer(text)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных действий для отмены")
        return
    await state.clear()
    await message.answer("Действие отменено")


def setup_handlers(dp):
    dp.include_router(router)


