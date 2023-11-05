import dash
from dash import html, dcc
from dash import dash_table
from dash.dependencies import Input, Output, State
from pymongo import MongoClient
import pandas as pd
from pandas import DataFrame
import plotly.express as px

# Connect to the MongoDB database
client = MongoClient("mongodb://127.0.0.1:27017/")
mydb = client["financial_data"]
collection = mydb["income_expense_savings"]
df=DataFrame(list(collection.find()))
print(df.head())
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

mongo_data = list(collection.find({}, {'_id': 0}))
df_mongo = pd.DataFrame(mongo_data)

# Calculate the sum of Amount for each Category
expense_data = df_mongo.groupby('Category')['Amount'].sum().reset_index()

# Create a pie chart
fig = px.pie(expense_data, names='Category', values='Amount', title='Expense Data')


# type form
app.layout = html.Div([
    html.Div([
        html.Label("Type"),
        
        dcc.Dropdown(options=[{'label': 'Income', 'value': 'Income'},
                             {'label': 'Expenses', 'value': 'Expenses'},
                             {'label': 'Savings', 'value': 'Savings'}],
                     id='type-dropdown'),
    ],style={'width':400}),
    
    # categorry form
    html.Div([
        html.Label("Category"),
       
        dcc.Dropdown(options=[{'label': 'Clothing', 'value': 'Clothing'},
                             {'label': 'Education', 'value': 'Education'},
                             {'label': 'Food', 'value': 'Food'},
                             {'label': 'Fuel', 'value': 'Fuel'},
                             {'label': 'Health', 'value': 'Health'},
                             {'label': 'Entertainment', 'value': 'Entertainment'},
                             {'label': 'Pets', 'value': 'Pets'},
                             {'label': 'Transport', 'value': 'Transport'},
                             {'label': 'Other', 'value': 'Other'}],
                     id='category-dropdown'),
    ],style={'width':400}),

    # amount form
    
    html.Div([
        html.Label("Amount"),
        dcc.Input(id="amount-input", type="number"),
    ], style={'width':400}),

    # save button
    html.Button("Save", id="save-it",style={'color':'red','background-color':'blue'}),
    html.Div(id="placeholder"),
  
    # displays data table
    html.Div([
    dcc.Graph(id='pie-chart', figure=fig),]),
    html.Div([ 
        dash_table.DataTable(
        id='mongo-datatable',
        columns=[
            {"name": "Type", "id": "Type"},
            {"name": "Category", "id": "Category"},
            {"name": "Amount", "id": "Amount"},
        ],
        page_size=10,  # Set the number of rows per page
        page_current=0,  # Set the initial page
        data=[],  # Initialize with empty data
    ),
])
    ])
   

    
# display mongo data on screen
@app.callback(Output('mongo-datatable', 'data'), Input('mongo-datatable', 'page_current'))
def populate_datatable(page_current):
    # Retrieve data from the MongoDB collection
    data = list(collection.find({}, {"_id": 0}))  # Exclude the "_id" field
    # Return the data for the current page
    return data[page_current * 10: (page_current + 1) * 10]

# save to mongoDB
@app.callback(Output("placeholder", "children"), Input("save-it", "n_clicks"), [State("type-dropdown", "value"), State("category-dropdown", "value"), State("amount-input", "value")], prevent_initial_call=True)
def save_data(n_clicks, data_type, category, amount):
    data = {
        "Type": data_type,
        "Category": category,
        "Amount": amount
    }
    collection.insert_one(data)
   
# run the app
if __name__ == '__main__':
    app.run_server(debug=True)