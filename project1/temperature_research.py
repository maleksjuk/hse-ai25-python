import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def _calculate_temperature_mean(city_data: pd.DataFrame):
    city_data = city_data.copy()
    city_data = city_data.sort_values('timestamp')
    city_data['temperature_mean'] = city_data['temperature'].rolling(30, 1).mean()
    return city_data


def add_temperature_mean(df: pd.DataFrame):
    return df.groupby('city', as_index=False) \
        .apply(_calculate_temperature_mean) \
        .droplevel(0).sort_index()


def get_season_stats(df: pd.DataFrame):
    season_stats = df.groupby(['city', 'season']).agg(
        mean=('temperature', 'mean'),
        std=('temperature', 'std')
    ).reset_index()
    season_stats['border_left'] = season_stats['mean'] - 2 * season_stats['std']
    season_stats['border_right'] = season_stats['mean'] + 2 * season_stats['std']
    return season_stats


def get_season_stats_for_show(season_stats: pd.DataFrame):
    rename_columns = {
        'season': 'Сезон',
        'mean': 'Средняя температура',
        'std': 'Стандартное отклонение',
    }
    show_season_stats = season_stats.rename(columns=rename_columns)
    return show_season_stats[rename_columns.values()]


def get_dataframe_with_anomalies(df: pd.DataFrame, stats: pd.DataFrame):
    data = pd.merge(df, stats, on=['city', 'season'])
    data['anomaly'] = \
        (data['temperature'] < data['border_left']) | \
        (data['temperature'] > data['border_right'])
    return data


def is_regular_temperature(temp: int | float, season: str, city_season_stats_with_borders: pd.DataFrame):
    df = city_season_stats_with_borders
    df = df[df['season'] == season]
    its_ok = df['border_left'].iloc[0] < temp < df['border_right'].iloc[0]
    return its_ok


def get_figure_for_city(city, city_data, anomaly_city_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=city_data['timestamp'],
        y=city_data['temperature'],
        mode='lines',
        line=dict(color='blue', width=0.8),
        name='Температура',
        opacity=0.8,
        hovertemplate='%{x}<br>%{y}°C<extra></extra>'
    ))

    if not anomaly_city_data.empty:
        fig.add_trace(go.Scatter(
            x=anomaly_city_data['timestamp'],
            y=anomaly_city_data['temperature'],
            mode='markers',
            marker=dict(
                color='red',
                size=5,
                symbol='circle',
                line=dict(color='darkred', width=1)
            ),
            name='Аномалии',
            hovertemplate='<b>Аномалия</b><br>%{x}<br>%{y}°C<extra></extra>'
        ))

    fig.add_trace(go.Scatter(
        x=city_data['timestamp'],
        y=city_data['temperature_mean'],
        mode='lines',
        line=dict(color='green', width=3),
        name='Среднее (30 дн)',
        opacity=0.5,
        hovertemplate='<b>Среднее (30 дн)</b>%{x}<br>%{y}°C<extra></extra>'
    ))


    fig.add_trace(go.Scatter(
        x=city_data['timestamp'],
        y=city_data['border_left'],
        mode='lines',
        line=dict(color='darkorange', width=2, dash='dash'),
        name='Нижнее отклонение за сезон',
        opacity=0.2,
        hovertemplate='<b>Нижнее отклонение</b>%{x}<br>%{y}°C<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=city_data['timestamp'],
        y=city_data['mean'],
        mode='lines',
        line=dict(color='darkorange', width=5),
        name='Среднее за сезон',
        opacity=0.3,
        hovertemplate='<b>Среднее за сезон</b>%{x}<br>%{y}°C<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=city_data['timestamp'],
        y=city_data['border_right'],
        mode='lines',
        line=dict(color='darkorange', width=2, dash='dash'),
        name='Верхнее отклонение за сезон',
        opacity=0.2,
        hovertemplate='<b>Верхнее отклонение</b>%{x}<br>%{y}°C<extra></extra>'
    ))
    
    dates = city_data['timestamp']
    fig.update_layout(
        title=f'Данные по температуре в городе {city}',
        legend_orientation='h',
        legend=dict(x=.5, xanchor='center', yanchor='top'),
        xaxis_title='Дата',
        yaxis_title='Температура (°C)',
        height=600,
        xaxis={
            'rangeslider': {'visible': True},
            'type': 'date',
            'showgrid': True,
            'range': [dates.iloc[-365], dates.iloc[-1]],
            'rangeslider': dict(visible=True),
        }
    )

    return fig
