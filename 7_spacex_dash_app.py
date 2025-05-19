# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                #dcc.Dropdown(id='site-dropdown',...)
                                html.Div(
                                    dcc.Dropdown(id='site-dropdown', 
                                                    options=[
                                                        {'label': 'All Sites', 'value': 'ALL'}
                                                    ] + [
                                                        {'label': site, 'value': site} for site in launch_sites
                                                    ],
                                                    value='ALL',
                                                    placeholder="place holder here",
                                                    searchable=True
                                                )
                                ),
                                html.Br(),
                                

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                           2500: '2500',
                                           5000: '5000',
                                           7500: '7500',
                                        10000: '10000'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        successes = spacex_df[spacex_df['class']==1]
        successes_by_site = successes.groupby('Launch Site').size().reset_index(name='Success Count')

        fig = px.pie(successes_by_site, values='Success Count', 
        names='Launch Site', 
        title='All Successes per Launch Site')

        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = filtered_df['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
        counts['Outcome'] = counts['Outcome'].replace({1: 'Success', 0: 'Failure'})

        fig = px.pie(counts, values='Count', 
        names='Outcome', 
        title=f'All Successes per {entered_site}')

        return fig
        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                [Input(component_id='site-dropdown', component_property='value'), 
                Input(component_id="payload-slider", component_property="value")]
               )
def get_scatter_plot(entered_site, selected_payload_range):

    min_payload, max_payload = selected_payload_range

    if entered_site == 'ALL':
        payload_selection = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                                      (spacex_df['Payload Mass (kg)'] <= max_payload)]
        title = 'Correlation between Payload and Success for all Sites'
        
    else:
        payload_selection = spacex_df[spacex_df['Launch Site'] == entered_site]
        payload_selection = payload_selection[(payload_selection['Payload Mass (kg)'] >= min_payload) & 
                                      (payload_selection['Payload Mass (kg)'] <= max_payload)]
        
        title = f'Correlation between Payload and Success for {entered_site}'
    fig = px.scatter(
            payload_selection,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title= title,
            labels={
                'Payload Mass (kg)': 'Payload Mass (kg)',
                'class': 'class'
            }, 
        )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
