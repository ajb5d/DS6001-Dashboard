from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df = pd.read_parquet("data/gss2018clean.parquet")

FILTER_COLS = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
STRATA_COLS = ['sex', 'region', 'education']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server

app.layout = html.Div([
    html.H1(children='2018 GSS Results', style={'textAlign':'center'}),
    html.Div(
        id = "left-col",
        className = "three columns",
        children = [
            dcc.Dropdown(FILTER_COLS, 'satjob', id='dropdown-feature'),
            dcc.Dropdown(STRATA_COLS, 'sex', id='dropdown-strata'),
        ]),
    html.Div(
        id = "right-col",
        className = "eight columns",
        children = [
            dcc.Graph(id='graph-content')
        ]
    )
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-feature', 'value'),
    Input('dropdown-strata', 'value')
)
def update_graph(feature, strata):
    figure_data = (
        df.groupby([strata, feature])
            .size()
            .reset_index()
            .rename({0: 'count'}, axis = 1)
    )

    plt = px.bar(
        figure_data,
        x=feature,
        y='count',
        color = strata,
        barmode='group')

    return plt

if __name__ == '__main__':
    app.run_server(debug=True)