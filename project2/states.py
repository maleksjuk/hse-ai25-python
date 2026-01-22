from aiogram.fsm.state import State, StatesGroup

class Profile(StatesGroup):
    weight = State()
    height = State()
    age = State()
    active_time = State()
    city = State()
    target = State()

class Calories(StatesGroup):
    name = State()
    count = State()

class FoodLogging(StatesGroup):
    food = State()
    count = State()

class WaterLogging(StatesGroup):
    count = State()
