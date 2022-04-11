import pandas as pd
import plotly.express as px
from dash import html, dcc

data = pd.DataFrame(columns=['time', 'user_id'])
data.to_csv('dashboard_data.csv', index=False)


def get_fig():
    data = pd.read_csv('dashboard_data.csv')
    fig = px.histogram(data, x='time')

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(step="all"),
                dict(count=1, label="day", step="day", stepmode="backward"),
                dict(count=7, label="week", step="day", stepmode="backward"),
                dict(count=1, label="month", step="month", stepmode="backward"),
            ])
        )
    )
    return fig


def serve_layout():
    fig = get_fig()

    graph = dcc.Graph(
        id='example-graph',
        figure=fig
    )
    graph.figure.layout.height = 800

    return html.Div(children=[
        graph
    ])


def new_event(time, user_id):
    data = pd.read_csv('dashboard_data.csv')
    data = pd.concat([data, pd.DataFrame([{'time': time.replace(hour=0, minute=0, second=0, microsecond=0), 'user_id': user_id}])], axis=0)
    data.to_csv('dashboard_data.csv', index=False)

