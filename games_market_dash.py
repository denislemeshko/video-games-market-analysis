from dash import Dash, html, dash_table, dcc, callback, Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd



# Загрузка датасета
df = pd.read_csv('vgsales.csv', encoding='ISO-8859-1')

# === Предобработка (исправлено под vgsales) ===
# В vgsales столбец называется 'Year', а не 'Year_of_Release'
# User_Score и Critic_Score в vgsales отсутствуют

# Фильтр: только игры с 2000 года и с известным годом
df = df[df['Year'] >= 2000]

# Удаляем строки с пропусками
df = df.dropna(how='any')

# Приводим Year к целому числу
df['Year'] = df['Year'].astype(int)

# Проверка
print("Строк после фильтра:", len(df))
print(df.head())

# Инициализируем Dash
app = Dash(__name__)

# Создаем макет
app.layout = html.Div([
    html.Div(html.H2('Интерактивный дешборд по играм', style={
        'text-align': 'center',
        'font-family': 'Open Sans, serif',
        'font-size': '36px',
        'font-weight': 'bold',
        'color': '#007BFF',
        'margin-top': '20px',
        'margin-bottom': '10px',
        'text-decoration': 'underline',
    })),
    html.Div(html.H4('В этом дашборде можно выбрать жанры, платформы, а также интервал годов выпуска', style={
        'text-align': 'center',
        'font-family': 'Open Sans, serif',
        'font-size': '24px',
        'color': '#444',
        'margin-bottom': '20px',
    })),
    html.Div([
        html.Label('Выбор жанра'),
        dcc.Checklist(
            id='Genre',
            options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique().tolist()],
            value=df['Genre'].unique().tolist(),
            labelStyle={'display': 'inline-block', 'color': '#444'}
        )
    ], style={'width': '45%', 'display': 'inline-block'}),

    html.Div([
        html.Label('Выбор платформы'),
        dcc.Checklist(
            id='Platform',
            options=[{'label': platform, 'value': platform} for platform in df['Platform'].unique().tolist()],
            value=df['Platform'].unique().tolist(),
            labelStyle={'display': 'inline-block', 'color': '#444'}
        )
    ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
    html.Div(
        id='chosen',
        style={
            'font-family': 'Open Sans, serif',
            'font-weight': 'bold',
            'width': '100%',
            'display': 'inline-block',
            'padding': '20px 0px 0px 20px',
            'text-align': 'center',
            'font-size': '20px'}
    ),

    html.Div(
        dcc.Graph(figure={}, id='stack_graph'),
        style={'width': '49%', 'display': 'inline-block'}
    ),

    html.Div(
        dcc.Graph(figure={}, id='scatter'),
        style={'width': '49%', 'float': 'right', 'display': 'inline-block'}
    ),

    html.Div([
        dcc.RangeSlider(
            min=min(df['Year']),
            max=max(df['Year']),
            step=None,
            value=[2005, 2014],
            id='year',
            marks={str(year): str(year) for year in df['Year'].unique()}
        ),
        html.Div(id='output-container-range-slider')
    ])
])


@app.callback(
    Output(component_id='chosen', component_property='children'),
    Output(component_id='stack_graph', component_property='figure'),
    Output(component_id='scatter', component_property='figure'),
    Input(component_id='Platform', component_property='value'),
    Input(component_id='Genre', component_property='value'),
    Input(component_id='year', component_property='value')
)
def update_graph(platform, genre, year):
    # Применение выбранных фильтров
    filtered_df = df[(df['Platform'].isin(platform)) &
                     (df['Genre'].isin(genre)) &
                     (df['Year'] >= year[0]) &
                     (df['Year'] <= year[1])]


    stacked_df = pd.DataFrame(
        filtered_df.groupby(['Year', 'Platform'])['Name'].count()
    ).reset_index()

    fig_1 = px.area(stacked_df, x='Year', y='Name', color='Platform', line_group='Platform')

    # В vgsales нет User_Score и Critic_Score — используем продажи
    fig_2 = px.scatter(
        filtered_df,
        x='NA_Sales',
        y='Global_Sales',
        color='Genre',
        hover_data=['Name', 'Platform'],
        title='Продажи в Северной Америке vs Глобальные'
    )

    return f'Выбрано {len(filtered_df)} игр', fig_1, fig_2


# Запуск
if __name__ == '__main__':
    app.run(debug=True)

