import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, Patch, MATCH, ALLSMALLER, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import os
import time
from datetime import datetime

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

df = pd.read_csv('ia_50_full_list.csv', index_col=None)
#df_options = pd.read_csv('all_dropdown_options.csv', index_col=None)
#df_options.set_index('column', inplace=True)
df_links = pd.read_csv('ia_50_fund_links.csv', index_col=None)

default_table_style = {
    'overflowX': 'auto',
    'border': '1px solid #dee2e6',
    'borderCollapse': 'collapse',
    'width': '100%',
    'marginBottom': '0'
}

default_header_style = {
    'backgroundColor': '#f8f9fa',
    'fontWeight': 'bold',
    'border': '1px solid #dee2e6',
    'textAlign': 'center'
}

default_cell_style = {
    'textAlign': 'left',
    'padding': '8px',
    'border': '1px solid #dee2e6'
}

default_conditional_style = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgba(248, 248, 248, 0.8)'
    },
    {
        'if': {'row_index': 'even'},
        'backgroundColor': 'rgba(255, 255, 255, 0.8)'
    }
]

default_styles = {
    'style_table': default_table_style,
    'style_header': default_header_style,
    'style_cell': default_cell_style,
    'style_data_conditional': default_conditional_style
}

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
server = app.server

app.layout = html.Div(className='dbc', children=[
    dbc.Container(children=[
        dbc.Row(children=[
            html.H1('Impact Investment Firm Database Lookup', style={'textAlign': 'center'})
        ]),
        dbc.Row(children=[
            dbc.Col(children=[
                html.H3('Financial Info'),
                html.Div('AUM'),
                dcc.Dropdown(
                    options=df.loc[:, 'total_aum'].unique(),
                    id='aum-select'
                ),
                html.Div('Asset Class'),
                dcc.Dropdown(
                    # options=df.loc[:, 'asset_class'].unique(),
                    id='asset-class-select'
                ),
                html.Div('Target Return Benchmark'),
                dcc.Dropdown(
                    options=df.loc[:, 'target_return_bm'].unique(),
                    id='return-bm-select'
                ),
                html.Div('Target Return Performance'),
                dcc.Dropdown(
                    options=df.loc[:, 'target_return_perf'].unique(),
                    id='return-perf-select'
                ),
                html.Div('Total Investors'),
                dcc.Dropdown(
                    options=df.loc[:, 'total_investors'].unique(),
                    id='total-investors-select'
                ),
                html.Div('Capital from Top 3 Investors'),
                dcc.Dropdown(
                    options=df.loc[:, 'capital_from_top_3'].unique(),
                    id='capital-top-select'
                ),
            ], width=4),
            dbc.Col(children=[
                html.H3('Firm Information'),
                html.Div('Firm HQ Location'),
                dcc.Dropdown(
                    options=df.loc[:, 'firm_hq'].unique(),
                    id='firm-hq-select'
                ),
                html.Div('Years in Operation'),
                dcc.Dropdown(
                    options=df.loc[:, 'years_in_op'].unique(),
                    id='years-op-select'
                ),
                html.Div('Leadership Exp. in Impact'),
                dcc.Dropdown(
                    options=df.loc[:, 'lead_total_impact_exp'].unique(),
                    id='leader-impact-select'
                ),
                html.Div('% of Investment Team - Women'),
                dcc.Dropdown(
                    options=df.loc[:, 'pct_invest_women'].unique(),
                    id='invest-women-select'
                ),
                html.Div('% of Investment Team - POC'),
                dcc.Dropdown(
                    options=df.loc[:, 'pct_invest_poc'].unique(),
                    id='invest-poc-select'
                ),
                html.Div('% of Sr Management - Women'),
                dcc.Dropdown(
                    options=df.loc[:, 'pct_sr_mgmt_women'].unique(),
                    id='mgmt-women-select'
                ),
                html.Div('% of Sr Management - POC'),
                dcc.Dropdown(
                    options=df.loc[:, 'pct_sr_mgmt_poc'].unique(),
                    id='mgmt-poc-select'
                ),
            ], width=4),
            dbc.Col(children=[
                html.H3('Impact Information'),
                html.Div('Main SDG'),
                dcc.Dropdown(
                    options=df.loc[:, 'main_sdg'].unique(),
                    id='main-sdg-select'
                ),
                html.Div('Secondary SDG'),
                dcc.Dropdown(
                    # options=df.loc[:, 'secondary_sdg'].unique(),
                    id='secondary-sdg-select'
                ),
                html.Div('% of AUM in Impact'),
                dcc.Dropdown(
                    options=df.loc[:, 'pct_aum_impact'].unique(),
                    id='aum-impact-select'
                ),
                html.Div('Impact Verified'),
                dcc.Dropdown(
                    options=df.loc[:, 'impact_verified'].unique(),
                    id='impact-verify-select'
                ),
                html.Div('Impact Report Frequency'),
                dcc.Dropdown(
                    options=df.loc[:, 'impact_reported'].unique(),
                    id='impact-report-select'
                ),
            ], width=4)
        ]),
        dbc.Row(children=[
            dbc.Button('Generate Results', class_name={'color': 'ms-auto'}, n_clicks=0, id='generate-results'),
            html.H3('Search Results', style={'textAlign': 'center'}),
            html.Div('', id='search-results')
        ])
    ])
])


@app.callback(
    Output('search-results', 'children'),
    Input('generate-results', 'n_clicks'),
    [
        State('aum-select', 'value'),
        State('asset-class-select', 'value'),
        State('return-bm-select', 'value'),
        State('return-perf-select', 'value'),
        State('total-investors-select', 'value'),
        State('capital-top-select', 'value'),
        State('firm-hq-select', 'value'),
        State('years-op-select', 'value'),
        State('leader-impact-select', 'value'),
        State('invest-women-select', 'value'),
        State('invest-poc-select', 'value'),
        State('mgmt-women-select', 'value'),
        State('mgmt-poc-select', 'value'),
        State('main-sdg-select', 'value'),
        State('secondary-sdg-select', 'value'),
        State('aum-impact-select', 'value'),
        State('impact-verify-select', 'value'),
        State('impact-report-select', 'value')
    ]
)
def execute_search(n, aum, asset_class, return_bm, return_perf, total_investors, capital_top,
                   firm_hq, years_op, leader_impact, invest_women, invest_poc, mgmt_women, mgmt_poc,
                   main_sdg, secondary_sdg, aum_impact, impact_verify, impact_report):
    df_results = df.copy()
    inputs_list = [aum, asset_class, return_bm, return_perf, total_investors, capital_top,
                   firm_hq, years_op, leader_impact, invest_women, invest_poc, mgmt_women, mgmt_poc,
                   main_sdg, secondary_sdg, aum_impact, impact_verify, impact_report]
    columns_list = ['total_aum', 'asset_class', 'target_return_bm', 'target_return_perf', 'total_investors',
                    'capital_from_top_3', 'firm_hq', 'years_in_op', 'lead_total_impact_exp', 'pct_invest_women',
                    'pct_invest_poc', 'pct_sr_mgmt_women', 'pct_sr_mgmt_poc', 'main_sdg', 'secondary_sdg',
                    'pct_aum_impact', 'impact_verified', 'impact_reported']
    search_parameters = []
    for search_value, column_name in zip(inputs_list, columns_list):
        parameters_dict = {'column_name': column_name, 'search_item': search_value}
        search_parameters.append(parameters_dict)
    if n:
        for parameter in search_parameters:
            if len(df_results) > 0:
                if parameter['search_item'] is not None:
                    df_results = df_results[df_results[parameter['column_name']] == parameter['search_item']]
            else:
                results = 'No Impact Investment Firms Found'
                return results
    else:
        results = ''
        return results
    df_results_display = df_results[['name', 'website']]
    df_results_display = pd.merge(df_results_display, df_links, on='name')
    df_results_display.rename(columns={'name': 'Fund Name', 'website': 'Fund Website', 'link': 'IA 50 Summary'},
                              inplace=True)
    results = dash_table.DataTable(
        id='search-results-table',
        columns=[{'name': col, 'id': col} for col in df_results_display.columns],
        data=df_results_display.to_dict('records'),
        page_size=10,
        **default_styles
    )
    return results


if __name__ == '__main__':
    app.run_server(debug=True)
