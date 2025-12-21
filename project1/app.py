import streamlit as st
import requests
import pandas as pd
import temperature_research as tr
from datetime import datetime as dt


WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
TEMPERATURE_DATA_DEFAULT = None #'temperature_data.csv'

def wrap_response(data: dict | None = None, success: bool = True, error: int | str | None = None):
    return {
        'success': success,
        'data': data,
        'error': error
    }


def get_weather(api_key, city):
    url = f'{WEATHER_URL}?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return wrap_response(response.json())
    else:
        return wrap_response(success=False, error=response.status_code)


def get_dataframes(data: pd.DataFrame, city):
    season_stats = tr.get_season_stats(data)
    season_stats = season_stats[season_stats['city'] == city]\
        .reset_index(drop=True)
    city_data = data[data['city'] == city]
    city_data = tr.add_temperature_mean(city_data)
    city_data = tr.get_dataframe_with_anomalies(city_data, season_stats)\
        .reset_index(drop=True)
    anomaly_city_data = city_data[city_data['anomaly']]
    return season_stats, city_data, anomaly_city_data


def today_season():
    seasons = ['winter', 'spring', 'summer', 'autumn']
    index = dt.now().month // 3 % 4
    return seasons[index]


def main():
    st.set_page_config(page_title="Проект 1", layout="wide")
    st.title('Проект 1. Анализ температуры и мониторинг текущей температуры')

    with st.sidebar:
        st.subheader('Загрузка исторических данных')

        uploaded_file = st.file_uploader("Загрузите CSV файл", type=["csv"])
        if uploaded_file is None and TEMPERATURE_DATA_DEFAULT is not None:
            uploaded_file = TEMPERATURE_DATA_DEFAULT
        if uploaded_file is None:
            st.info("Загрузите CSV файл для начала работы")
            st.stop()
        else:
            try:
                data = pd.read_csv(uploaded_file)
            except:
                st.write(f'Ошибка загрузки файла "{uploaded_file}"')
                st.stop()

        API_KEY = st.text_input('API-ключ OpenWeatherMap')

    

    column1, column2 = st.columns([0.3, 0.7])

    with column1:

        selected_city = st.selectbox(
            'Выберите город',
            data['city'].unique(),
            index=None
        )

        if selected_city:
            season_stats, city_data, anomaly_city_data = get_dataframes(data, selected_city)

            st.subheader(f'Сейчас в {selected_city}')
            if API_KEY:
                weather_data = get_weather(API_KEY, selected_city)
                if weather_data['success']:
                    current_temperature = weather_data['data']['main']['temp']
                    st.title(f'{current_temperature}°C', text_alignment='center')
                    is_regular_temp = tr.is_regular_temperature(current_temperature, today_season(), city_data)
                    regular_label = "нормальная" if is_regular_temp else "аномальная"
                    color = 'darkgreen' if is_regular_temp else 'red'
                    st.markdown(f'Это __<span style="color:{color}">{regular_label}</span>__ температура для **{today_season()}** в этом городе', unsafe_allow_html=True)
                else:
                    if weather_data['error'] == 401:
                        st.error('Неправильный API-ключ')
            else:
                st.badge('Введите ключ API OpenWeatherMap', color='yellow')

    with column2:
        if selected_city:
            st.subheader('Статистика по историческим данным для города')
            st.table(tr.get_season_stats_for_show(season_stats))
            fig = tr.get_figure_for_city(selected_city, city_data, anomaly_city_data)
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
