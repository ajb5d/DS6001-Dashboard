from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.io as pio
import pandas as pd
from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()

df = pd.read_parquet(THIS_FOLDER / "data" / "gss2018clean.parquet")

pio.templates.default = "plotly_white"

# * `sex` - male or female
# * `education` - years of formal education
# * `region` - region of the country where the respondent lives
# * `job_prestige` - the respondent's occupational prestige score, as measured by the GSS using the methodology described above
# * `satjob` - responses to "On the whole, how satisfied are you with the work you do?"
# * `relationship` - agree or disagree with: "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work."
# * `male_breadwinner` - agree or disagree with: "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."
# * `men_bettersuited` - agree or disagree with: "Most men are better suited emotionally for politics than are most women."
# * `child_suffer` - agree or disagree with: "A preschool child is likely to suffer if his or her mother works."
# * `men_overwork` - agree or disagree with: "Family life often suffers because men concentrate too much on their work."

FILTER_COLS = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
STRATA_COLS = ['sex', 'region', 'education']
LABELS = {
    'satjob': 'Overall Job Satistfaction',
    'relationship': 'Agreement with: "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work."',
    'male_breadwinner': 'Agreement with: "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."',
    'men_bettersuited': 'Agreement with: "Most men are better suited emotionally for politics than are most women."',
    'child_suffer': 'Agreement with: "A preschool child is likely to suffer if his or her mother works."',
    'men_overwork': 'Agreement with: "Family life often suffers because men concentrate too much on their work."',
    'sex': 'Respondent\'s sex',
    'region': 'Respondent\'s home region',
    'education': 'Respondent\'s years of formal education',
    'count': 'Count of Responses',
    'grppct': 'Percentage of Strata',
    'overall_pct': 'Percentage of Total Responses',
    'rowpct': 'Percentage of Each Categorical Response',
    'male': 'Male'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server

label_style = {
    'font-weight': 'bold'
}

app.layout = html.Div([
    html.H1(children='2018 GSS Results', style={'textAlign':'center'}),
    dcc.Graph(id='graph-content'),
    html.Div(
        id = "left-col",
        className = "three columns",
        children = [
            html.Div(
                children  =[
                    html.Label("Strata:", style = label_style),
                    dcc.RadioItems({k: LABELS[k] for k in STRATA_COLS}, 'sex', id='dropdown-strata'),
                ]
            ),
            html.Div(
                children = [
                    html.Label("Y-Axis:", style = label_style),
                    dcc.RadioItems(
                    {
                        'count': 'Count of responses',
                        'grppct': 'Precentage of Strata',
                        'rowpct': 'Percentage of Response',
                        'overall_pct': 'Overall Percentage',
                    },
                    'count', 
                    inline=True,
                    id='radio-options')
                ]
            )

        ]),
    html.Div(
        id = "right-col",
        className = "eight columns",
        children = [
            html.Label('Question (X-axis):', style = label_style),
            dcc.Dropdown({k: LABELS[k] for k in FILTER_COLS}, 'satjob', id='dropdown-feature')
        ]
    ),
    dcc.Markdown("by Andrew Barros [source](https://github.com/ajb5d/DS6001-Dashboard)", className = "offset-by-five columns")
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-feature', 'value'),
    Input('dropdown-strata', 'value'),
    Input('radio-options', 'value')
)
def update_graph(feature, strata, metric):
    strata_totals = (
        df.groupby(strata)
            .size()
            .reset_index()
            .rename({0: 'strata_total'}, axis = 1)
    )

    row_totals = (
        df.groupby(feature)
            .size()
            .reset_index()
            .rename({0: 'row_total'}, axis = 1)
    )

    figure_data = (
        df.groupby([strata, feature])
            .size()
            .reset_index()
            .rename({0: 'count'}, axis = 1)
            .join(strata_totals.set_index(strata), on = strata)
            .join(row_totals.set_index(feature), on = feature)
    )

    figure_data['grppct'] = figure_data['count'] / figure_data['strata_total']
    figure_data['rowpct'] = figure_data['count'] / figure_data['row_total']
    figure_data['overall_pct'] = figure_data['count'] / figure_data['count'].sum()
    

    plt = px.bar(
        figure_data,
        x=feature,
        y=metric,
        labels = LABELS,
        color = strata,
        barmode='group')
    
    if metric in ['grppct', 'overall_pct', 'rowpct']:
        plt.update_layout(yaxis_tickformat = '2.0~%')

    return plt

if __name__ == '__main__':
    app.run_server(debug=True)