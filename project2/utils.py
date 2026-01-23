import aiohttp
from random import randint

async def get_product_calories(product_name: str):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # print(response)
            if not response.ok:
                return None
            data = await response.json()
            products = data.get('products', [])
            if products:
                first_product = products[0]
                return {
                    'name': first_product.get('product_name', 'Неизвестно'),
                    'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
                }
            return None


async def get_temperature(city: str, api_key: str):
    WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
    url = f'{WEATHER_URL}?q={city}&appid={api_key}&units=metric'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # print(response)
            if not response.ok:
                return None
            return await response.json()


async def get_workout_calories(workout: str):
    """
    Я не смог быстро найти API для определения данных по тренировке. Поэтому будет рандом
    """
    burned_calories = len(workout) * randint(100, 1000) % 1500
    return burned_calories
