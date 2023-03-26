from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import networks
from networks import Vill_Net


app = Dash(__name__)

# Styles and constants
colors = {
    'background': '#FDFEFE',
    'text': '#17202A'
}

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Layout of the app
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.Div([
        html.H2(children='Visualizing take up of microfinance across a village in Karnataka, India'),

        html.Div(children='''
            More explanation
        '''), 
    ]), 

    html.Div([
    dcc.Dropdown(
        id='name-dropdown',
        options=[
            {'label': '1', 'value': '1'},
            {'label': '2', 'value': '2'},
            {'label': '3', 'value': '3'},
        ],
        value='1',
    ),
    html.Div(id='output-div')
])
])

# Dynamic callback functions
@app.callback(
    Output('output-div', 'children'),
    Input('name-dropdown', 'value'))
def generate_figures(value):
    file = 'data/adj_allVillageRelationships_HH_vilno_' + str(value) + '.csv'
    v = Vill_Net(file, int(value))
    plots = v.gen_plots()
    all_plots = []
    for i in range(len(plots)):
        all_plots.append(dcc.Graph(
            id="graph" + str(i),
            style={'width': '40%', 'display':'inline-block'},
            figure=plots[i]
            ),)
    return all_plots


if __name__ == '__main__':
    app.run_server(debug=True)