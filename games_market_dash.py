from dash import Dash, html, dash_table, dcc, callback, Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


df = pd.read_csv('games.csv')
# Предобработка
df = df[(df['Year_of_Release'] >= 2000) & (df['User_Score'] != 'tbd')]
df = df.dropna(how='any')
df['Year_of_Release'] = df['Year_of_Release'].astype(int)
df['User_Score'] = df['User_Score'].astype(float)

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
    html.Div(html.H4('В этом дашборде можно выбрать жанры, рейтинг, а также интервал годов выпуска', style={
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
        html.Label('Выбор рейтинга'),
        dcc.Checklist(
            id='Rating',
            options=[{'label': rating, 'value': rating} for rating in df['Rating'].unique().tolist()],
            value=df['Rating'].unique().tolist(),
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
            min=min(df['Year_of_Release']),
            max=max(df['Year_of_Release']),
            step=None,
            value=[2005, 2014],
            id='year',
            marks={str(year): str(year) for year in df['Year_of_Release'].unique()}
        ),
        html.Div(id='output-container-range-slider')
    ])
])


@app.callback(
    Output(component_id='chosen', component_property='children'),
    Output(component_id='stack_graph', component_property='figure'),
    Output(component_id='scatter', component_property='figure'),
    Input(component_id='Rating', component_property='value'),
    Input(component_id='Genre', component_property='value'),
    Input(component_id='year', component_property='value')
)
def update_graph(rating, genre, year):
    # Применение выбранных фильтров
    filtered_df = df[(df['Rating'].isin(rating)) &
                     (df['Genre'].isin(genre)) &
                     (df['Year_of_Release'] > year[0]) &
                     (df['Year_of_Release'] < year[1])]


    stacked_df = pd.DataFrame(
        filtered_df.groupby(['Year_of_Release', 'Platform'])['Name'].count()
    ).reset_index()

    fig_1 = px.area(stacked_df, x='Year_of_Release', y='Name', color='Platform', line_group='Platform')

    fig_2 = px.scatter(filtered_df, x='User_Score', y='Critic_Score', color='Genre')

    return f'Выбрано {len(filtered_df)} игр', fig_1, fig_2


# Запуск
if __name__ == '__main__':
    app.run(debug=True)
