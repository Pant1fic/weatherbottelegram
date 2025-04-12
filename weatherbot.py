import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import requests
import datetime
from dotenv import load_dotenv
import logging
import math

# Загрузка переменных окружения
load_dotenv()

# Настройка логов и логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфиг(вставляете свои токены)
TELEGRAM_TOKEN = ("YOUR_TELEGRAM_TOKEN") # Telegram токен
OPENWEATHER_API_KEY = ("YOUR_OPENWEATHER_API_KEY") # API для погоды
AIRVISUAL_API_KEY = ("YOUR_AIRVISUAL_API_KEY")  # API для качества воздуха

# Настройки пагинации(сколько городов отображается на 1 странице)
CITIES_PER_PAGE = 6

# Список городов России с координатами(не трогать)
CITIES = {
    "Москва": {"lat": 55.7558, "lon": 37.6173},
    "Санкт-Петербург": {"lat": 59.9343, "lon": 30.3351},
    "Новосибирск": {"lat": 55.0084, "lon": 82.9357},
    "Екатеринбург": {"lat": 56.8389, "lon": 60.6057},
    "Казань": {"lat": 55.7961, "lon": 49.1064},
    "Нижний Новгород": {"lat": 56.3269, "lon": 44.0065},
    "Челябинск": {"lat": 55.1644, "lon": 61.4368},
    "Самара": {"lat": 53.1959, "lon": 50.1002},
    "Омск": {"lat": 54.9914, "lon": 73.3645},
    "Ростов-на-Дону": {"lat": 47.2357, "lon": 39.7015},
    "Уфа": {"lat": 54.7351, "lon": 55.9587},
    "Красноярск": {"lat": 56.0184, "lon": 92.8672},
    "Пермь": {"lat": 58.0105, "lon": 56.2294},
    "Воронеж": {"lat": 51.6606, "lon": 39.2003},
    "Волгоград": {"lat": 48.7194, "lon": 44.5018},
    "Краснодар": {"lat": 45.0355, "lon": 38.9753},
    "Саратов": {"lat": 51.5336, "lon": 46.0342},
    "Тюмень": {"lat": 57.1522, "lon": 65.5272},
    "Тольятти": {"lat": 53.5078, "lon": 49.4204},
    "Ижевск": {"lat": 56.8527, "lon": 53.2115},
    "Барнаул": {"lat": 53.3561, "lon": 83.7646},
    "Ульяновск": {"lat": 54.3142, "lon": 48.4031},
    "Иркутск": {"lat": 52.2864, "lon": 104.2807},
    "Хабаровск": {"lat": 48.4802, "lon": 135.0719},
    "Ярославль": {"lat": 57.6261, "lon": 39.8845},
    "Владивосток": {"lat": 43.1155, "lon": 131.8855},
    "Махачкала": {"lat": 42.9849, "lon": 47.5046},
    "Томск": {"lat": 56.4846, "lon": 84.9476},
    "Оренбург": {"lat": 51.7682, "lon": 55.0970},
    "Кемерово": {"lat": 55.3543, "lon": 86.0898},
    "Новокузнецк": {"lat": 53.7865, "lon": 87.1552},
    "Рязань": {"lat": 54.6294, "lon": 39.7417},
    "Астрахань": {"lat": 46.3479, "lon": 48.0336},
    "Набережные Челны": {"lat": 55.7436, "lon": 52.3958},
    "Пенза": {"lat": 53.1950, "lon": 45.0183},
    "Липецк": {"lat": 52.6088, "lon": 39.5992},
    "Киров": {"lat": 58.6036, "lon": 49.6680},
    "Чебоксары": {"lat": 56.1439, "lon": 47.2489},
    "Тула": {"lat": 54.1930, "lon": 37.6173},
    "Калининград": {"lat": 54.7104, "lon": 20.4522},
    "Балашиха": {"lat": 55.8094, "lon": 37.9581},
    "Курск": {"lat": 51.7304, "lon": 36.1926},
    "Ставрополь": {"lat": 45.0445, "lon": 41.9691},
    "Улан-Удэ": {"lat": 51.8335, "lon": 107.5841},
    "Сочи": {"lat": 43.5855, "lon": 39.7231},
    "Брянск": {"lat": 53.2436, "lon": 34.3634},
    "Сургут": {"lat": 61.2540, "lon": 73.3962},
    "Владимир": {"lat": 56.1290, "lon": 40.4070},
    "Чита": {"lat": 52.0339, "lon": 113.4994},
    "Архангельск": {"lat": 64.5393, "lon": 40.5187},
    "Смоленск": {"lat": 54.7826, "lon": 32.0453},
    "Калуга": {"lat": 54.5138, "lon": 36.2612},
    "Волжский": {"lat": 48.7939, "lon": 44.7736},
    "Череповец": {"lat": 59.1265, "lon": 37.9092},
    "Орёл": {"lat": 52.9703, "lon": 36.0635},
    "Вологда": {"lat": 59.2205, "lon": 39.8916},
    "Саранск": {"lat": 54.1874, "lon": 45.1839},
    "Мурманск": {"lat": 68.9707, "lon": 33.0749},
    "Якутск": {"lat": 62.0278, "lon": 129.7315},
    "Грозный": {"lat": 43.3180, "lon": 45.6982},
    "Стерлитамак": {"lat": 53.6306, "lon": 55.9306},
    "Кострома": {"lat": 57.7677, "lon": 40.9264},
    "Петрозаводск": {"lat": 61.7849, "lon": 34.3469},
    "Йошкар-Ола": {"lat": 56.6344, "lon": 47.8999},
    "Новороссийск": {"lat": 44.7235, "lon": 37.7686},
    "Сыктывкар": {"lat": 61.6688, "lon": 50.8364},
    "Нальчик": {"lat": 43.4853, "lon": 43.6071},
    "Шахты": {"lat": 47.7085, "lon": 40.2160},
    "Нижневартовск": {"lat": 60.9397, "lon": 76.5694},
    "Бийск": {"lat": 52.5414, "lon": 85.2196},
    "Орск": {"lat": 51.2293, "lon": 58.4752},
    "Ангарск": {"lat": 52.5449, "lon": 103.8885},
    "Королёв": {"lat": 55.9162, "lon": 37.8545},
    "Люберцы": {"lat": 55.6814, "lon": 37.8935},
    "Мытищи": {"lat": 55.9104, "lon": 37.7366},
    "Прокопьевск": {"lat": 53.8954, "lon": 86.7447},
    "Благовещенск": {"lat": 50.2907, "lon": 127.5272},
    "Старый Оскол": {"lat": 51.2967, "lon": 37.8417},
    "Златоуст": {"lat": 55.1711, "lon": 59.6728},
    "Электросталь": {"lat": 55.7842, "lon": 38.4534},
    "Миасс": {"lat": 55.0474, "lon": 60.1077},
    "Бердск": {"lat": 54.7586, "lon": 83.0926},
    "Находка": {"lat": 42.8240, "lon": 132.8928},
    "Рубцовск": {"lat": 51.5147, "lon": 81.2061},
    "Альметьевск": {"lat": 54.9014, "lon": 52.2973},
    "Ковров": {"lat": 56.3575, "lon": 41.3170},
    "Коломна": {"lat": 55.0794, "lon": 38.7783},
    "Майкоп": {"lat": 44.6054, "lon": 40.1005},
    "Пятигорск": {"lat": 44.0425, "lon": 43.0584},
    "Одинцово": {"lat": 55.6784, "lon": 37.2785},
    "Копейск": {"lat": 55.1168, "lon": 61.6256},
    "Химки": {"lat": 55.8970, "lon": 37.4297},
    "Серпухов": {"lat": 54.9139, "lon": 37.4117},
    "Новочебоксарск": {"lat": 56.1214, "lon": 47.4925},
    "Нефтеюганск": {"lat": 61.0998, "lon": 72.6035},
    "Димитровград": {"lat": 54.2376, "lon": 49.5896},
    "Назрань": {"lat": 43.2265, "lon": 44.7656},
    "Каменск-Уральский": {"lat": 56.4149, "lon": 61.9189},
    "Орехово-Зуево": {"lat": 55.8067, "lon": 38.9618},
    "Дербент": {"lat": 42.0674, "lon": 48.2890},
    "Невинномысск": {"lat": 44.6337, "lon": 41.9443},
    "Кызыл": {"lat": 51.7191, "lon": 94.4378},
    "Обнинск": {"lat": 55.0944, "lon": 36.6122},
    "Елец": {"lat": 52.6207, "lon": 38.5030},
    "Батайск": {"lat": 47.1396, "lon": 39.7518},
    "Северодвинск": {"lat": 64.5582, "lon": 39.8296},
    "Новомосковск": {"lat": 54.0333, "lon": 38.2666},
    "Железнодорожный": {"lat": 55.7504, "lon": 38.0042},
    "Сергиев Посад": {"lat": 56.3100, "lon": 38.1326},
    "Арзамас": {"lat": 55.3875, "lon": 43.8144},
    "Элиста": {"lat": 46.3078, "lon": 44.2558},
    "Новошахтинск": {"lat": 47.7579, "lon": 39.9364},
    "Балаково": {"lat": 52.0278, "lon": 47.8007},
    "Ногинск": {"lat": 55.8525, "lon": 38.4388},
    "Щёлково": {"lat": 55.9214, "lon": 37.9978},
    "Междуреченск": {"lat": 53.6866, "lon": 88.0704},
    "Кисловодск": {"lat": 43.9052, "lon": 42.7168},
    "Ессентуки": {"lat": 44.0444, "lon": 42.8649},
    "Раменское": {"lat": 55.5704, "lon": 38.2300},
    "Домодедово": {"lat": 55.4366, "lon": 37.7666},
    "Жуковский": {"lat": 55.5991, "lon": 38.1163},
    "Реутов": {"lat": 55.7585, "lon": 37.8616},
    "Назрановский район": {"lat": 43.2000, "lon": 44.7667},
    "Пушкино": {"lat": 56.0106, "lon": 37.8473}
}
#Уровни качества воздуха
AQI_LEVELS = {
    1: {"label": "Отлично", "emoji": "😊", "description": "Качество воздуха считается удовлетворительным"},
    2: {"label": "Хорошо", "emoji": "🙂", "description": "Качество воздуха приемлемое"},
    3: {"label": "Удовлетворительно", "emoji": "😐", "description": "Может влиять на чувствительных людей"},
    4: {"label": "Плохо", "emoji": "😷", "description": "Может влиять на всех"},
    5: {"label": "Очень плохо", "emoji": "⚠️", "description": "Опасное воздействие на всех"},
}

# Кэш для хранения данных пользователей
user_data = {}
#кнопки
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🌤 Текущая погода", callback_data="current"),
         InlineKeyboardButton("📅 Прогноз на 5 дней", callback_data="forecast")],
        [InlineKeyboardButton("🌫 Качество воздуха", callback_data="air_quality"),
         InlineKeyboardButton("🏙 Сменить город", callback_data="change_city")],
        [InlineKeyboardButton("⭐ Избранное", callback_data="favorites"),
         InlineKeyboardButton("🔄 Обновить", callback_data="refresh")],
    ]
    return InlineKeyboardMarkup(keyboard)

def cities_keyboard(user_id, page=0):
    """Клавиатура с пагинацией для выбора города"""
    keyboard = []
    city_list = list(CITIES.keys())
    total_pages = math.ceil(len(city_list) / CITIES_PER_PAGE)
    
    start_idx = page * CITIES_PER_PAGE
    end_idx = start_idx + CITIES_PER_PAGE
    page_cities = city_list[start_idx:end_idx]
    
    for city in page_cities:
        row = [InlineKeyboardButton(city, callback_data=f"city_{city}")]
        if city not in user_data.get(user_id, {}).get("favorites", []):
            row.append(InlineKeyboardButton("⭐", callback_data=f"add_fav_{city}"))
        keyboard.append(row)
    
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"prev_page_{page}"))
    if page < total_pages - 1:
        navigation.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"next_page_{page}"))
    
    if navigation:
        keyboard.append(navigation)
    
    keyboard.append([InlineKeyboardButton("🔙 В главное меню", callback_data="back")])
    
    return InlineKeyboardMarkup(keyboard)

def get_day_name(date):
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    return days[date.weekday()]

def get_weather_emoji(icon_code):
    icons = {
        "01": "☀️", "02": "⛅️", "03": "☁️", "04": "☁️",
        "09": "🌧", "10": "🌦", "11": "⛈", "13": "❄️", "50": "🌫"
    }
    return icons.get(icon_code[:2], "🌤")

async def get_weather_data(lat, lon):
    """Получение данных о погоде через API OpenWeather"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при запросе погоды: {e}")
        return None

async def get_air_quality(lat, lon):
    """Получение данных о качестве воздуха через AirVisual API"""
    try:
        url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={AIRVISUAL_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' not in data or 'current' not in data['data'] or 'pollution' not in data['data']['current']:
            logger.error("Неправильная структура ответа от AirVisual API")
            return None
            
        return data
    except Exception as e:
        logger.error(f"Ошибка при запросе качества воздуха: {e}")
        return None

async def send_current_weather(query, city, lat, lon):
    """Отправка текущей погоды"""
    weather_data = await get_weather_data(lat, lon)
    
    if not weather_data or 'list' not in weather_data or 'city' not in weather_data:
        await query.edit_message_text(
            text=" Не удалось получить данные о погоде",
            reply_markup=main_menu_keyboard()
        )
        return
    
    current = weather_data['list'][0]
    temp = current['main']['temp']
    feels_like = current['main']['feels_like']
    humidity = current['main']['humidity']
    pressure = current['main']['pressure']
    wind_speed = current['wind']['speed']
    description = current['weather'][0]['description']
    icon = current['weather'][0]['icon']
    
    sunrise = datetime.datetime.fromtimestamp(weather_data['city']['sunrise']).strftime('%H:%M')
    sunset = datetime.datetime.fromtimestamp(weather_data['city']['sunset']).strftime('%H:%M')
    
    message = (
        f" <b>Погода в {city}</b>\n\n"
        f"{get_weather_emoji(icon)} {description.capitalize()}\n"
        f"Температура: <b>{temp:.1f}°C</b> (ощущается как {feels_like:.1f}°C)\n"
        f" Влажность: {humidity}%\n"
        f" Давление: {pressure} гПа\n"
        f" Ветер: {wind_speed} м/с\n\n"
        f" Восход: {sunrise}\n"
        f" Закат: {sunset}\n\n"
        f"<i>Обновлено: {datetime.datetime.now().strftime('%H:%M %d.%m.%Y')}</i>"
    )
    
    await query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )

async def send_weather_forecast(query, city, lat, lon):
    """Отправка прогноза на 5 дней"""
    weather_data = await get_weather_data(lat, lon)
    
    if not weather_data or 'list' not in weather_data:
        await query.edit_message_text(
            text=" Не удалось получить прогноз погоды",
            reply_markup=main_menu_keyboard()
        )
        return
    
    message = f"<b>Прогноз погоды в {city} на 5 дней</b>\n\n"
    
    forecasts = {}
    for forecast in weather_data['list']:
        date = datetime.datetime.fromtimestamp(forecast['dt']).strftime('%d.%m')
        if date not in forecasts:
            forecasts[date] = []
        forecasts[date].append(forecast)
    
    for date, day_forecasts in forecasts.items():
        day_name = get_day_name(datetime.datetime.fromtimestamp(day_forecasts[0]['dt']))
        temp_min = min(f['main']['temp_min'] for f in day_forecasts)
        temp_max = max(f['main']['temp_max'] for f in day_forecasts)
        description = day_forecasts[0]['weather'][0]['description']
        icon = day_forecasts[0]['weather'][0]['icon']
        
        message += (
            f"\n<b>{day_name}, {date}</b>\n"
            f"{get_weather_emoji(icon)} {description.capitalize()}\n"
            f"🌡 Температура: от {temp_min:.1f}°C до {temp_max:.1f}°C\n"
        )
    
    message += f"\n<i>Обновлено: {datetime.datetime.now().strftime('%H:%M %d.%m.%Y')}</i>"
    
    await query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )

async def send_air_quality(query, city, lat, lon):
    """Отправка информации о качестве воздуха (только AQI)"""
    air_data = await get_air_quality(lat, lon)
    
    if not air_data or 'data' not in air_data or 'current' not in air_data['data'] or 'pollution' not in air_data['data']['current']:
        await query.edit_message_text(
            text=" Не удалось получить данные о качестве воздуха",
            reply_markup=main_menu_keyboard()
        )
        return
    
    pollution = air_data['data']['current']['pollution']
    aqi = pollution.get('aqius', 0)
    level = AQI_LEVELS.get(min(max(1, (aqi // 50) + 1), 5), AQI_LEVELS[5])
    
    message = (
        f"🌫 <b>Качество воздуха в {city}</b>\n\n"
        f"{level['emoji']} <b>Индекс AQI: {aqi} ({level['label']})</b>\n"
        f"{level['description']}\n\n"
        f"<i>Обновлено: {datetime.datetime.now().strftime('%H:%M %d.%m.%Y')}</i>"
    )
    
    await query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    user_id = update.effective_user.id
    user_data[user_id] = {"city": "Москва", "page": 0, "favorites": []}
    
    await update.message.reply_text(
        "🌤 Добро пожаловать!\n"
        "Выберите действие:",
        reply_markup=main_menu_keyboard()
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_data:
        user_data[user_id] = {"city": "Кемерово", "page": 0, "favorites": []}
    
    city = user_data[user_id]["city"]
    lat = CITIES[city]["lat"]
    lon = CITIES[city]["lon"]
    
    if data == "current":
        await send_current_weather(query, city, lat, lon)
    elif data == "forecast":
        await send_weather_forecast(query, city, lat, lon)
    elif data == "air_quality":
        await send_air_quality(query, city, lat, lon)
    elif data == "change_city":
        user_data[user_id]["page"] = 0
        await query.edit_message_text(
            text="🏙 Выберите город:",
            reply_markup=cities_keyboard(user_id)
        )
    elif data.startswith("city_"):
        selected_city = data[5:]
        user_data[user_id]["city"] = selected_city
        await query.edit_message_text(
            text=f"🌆 Выбран город: {selected_city}",
            reply_markup=main_menu_keyboard()
        )
    elif data.startswith("prev_page_"):
        page = int(data[10:]) - 1
        user_data[user_id]["page"] = page
        await query.edit_message_text(
            text="🏙 Выберите город:",
            reply_markup=cities_keyboard(user_id, page)
        )
    elif data.startswith("next_page_"):
        page = int(data[10:]) + 1
        user_data[user_id]["page"] = page
        await query.edit_message_text(
            text="🏙 Выберите город:",
            reply_markup=cities_keyboard(user_id, page)
        )
    elif data == "back":
        await query.edit_message_text(
            text="Выберите действие:",
            reply_markup=main_menu_keyboard()
        )
    elif data == "refresh":
        await query.edit_message_text(
            text="🔄 Обновляю данные...",
            reply_markup=main_menu_keyboard(),
        )
        await send_current_weather(query, city, lat, lon)
    elif data == "favorites":
        await show_favorites_menu(query)
    elif data.startswith("add_fav_"):
        city_to_add = data[8:]
        await add_to_favorites(query, city_to_add)
    elif data.startswith("remove_fav_"):
        city_to_remove = data[11:]
        await remove_from_favorites(query, city_to_remove)

async def show_favorites_menu(query):
    """Показать меню избранного"""
    user_id = query.from_user.id
    favorites = user_data.get(user_id, {}).get("favorites", [])
    
    if not favorites:
        await query.edit_message_text(
            text="⭐ У вас пока нет избранных городов",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить город в избранное", callback_data="change_city")],
                [InlineKeyboardButton("🔙 В главное меню", callback_data="back")]
            ])
        )
    else:
        keyboard = []
        for city in favorites:
            keyboard.append([InlineKeyboardButton(city, callback_data=f"city_{city}")])
        
        keyboard.append([InlineKeyboardButton("🔙 В главное меню", callback_data="back")])
        
        await query.edit_message_text(
            text="⭐ Ваши избранные города:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def add_to_favorites(query, city):
    """Добавить город в избранное"""
    user_id = query.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {"favorites": []}
    elif "favorites" not in user_data[user_id]:
        user_data[user_id]["favorites"] = []
    
    if city not in user_data[user_id]["favorites"]:
        user_data[user_id]["favorites"].append(city)
        await query.answer(f"Город {city} добавлен в избранное!")
    else:
        await query.answer("Этот город уже в избранном")
    
    await show_favorites_menu(query)

async def remove_from_favorites(query, city):
    """Удалить город из избранного"""
    user_id = query.from_user.id
    
    if user_id in user_data and "favorites" in user_data[user_id]:
        if city in user_data[user_id]["favorites"]:
            user_data[user_id]["favorites"].remove(city)
            await query.answer(f"Город {city} удален из избранного")
    
    await show_favorites_menu(query)

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
