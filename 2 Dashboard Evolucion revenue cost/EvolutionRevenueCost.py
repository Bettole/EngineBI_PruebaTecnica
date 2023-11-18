import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

pd.options.display.float_format = '{:,.2f}'.format

# Cargar datos desde archivos CSV
df_ingresos = pd.read_csv('revenue_2022.csv')
df_costos = pd.read_csv('costs_2022.csv')

# Crea diccionarios para los meses
meses = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Diccionario para ordenamiento de meses
ordenMeses = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

### Limpieza datos ####
### Revenue

# UnPivot
df_ingresos_pivot = pd.melt(df_ingresos, id_vars=['Line Of Business'], var_name='month', value_name='value',
                            value_vars=meses)
df_ingresos_pivot['value'] = df_ingresos_pivot['value'].str.replace('$', '', regex=False)
df_ingresos_pivot['value'] = df_ingresos_pivot['value'].str.replace(',', '', regex=False)
df_ingresos_pivot['value'] = df_ingresos_pivot['value'].astype(float)
df_ingresos_pivot['tipo'] = 'Revenue'

#Realizando exploración de datos, se encuentra revenue negativo, por lo que es importante indagar primero con cliente si de debe aislar o realizar un ajuste.
#Sin embargo se aisla.
df_ingresos_pivot = df_ingresos_pivot[df_ingresos_pivot['value']>0]

### Cost

# UnPivot
df_costos_pivot = pd.melt(df_costos, id_vars=['Line Of Business'], var_name='month', value_name='value',
                          value_vars=meses)
df_costos_pivot['value'] = pd.to_numeric(df_costos_pivot['value'], errors='coerce')
df_costos_pivot['tipo'] = 'Cost'
df_costos_pivot['value'] *= -1

##------ Union Revenue and Cost
df_data = pd.concat([df_ingresos_pivot, df_costos_pivot])

# Agrega 'ordenMes' utilizando diccionario de orden
df_data['ordenMes'] = df_data['month'].map(ordenMeses)

# Ordenamiento por "Line Of Business" y "ordenMes" para calcular la variación con respecto al mes anterior LM = LastMonth
df_data_agg = df_data.groupby(['ordenMes', 'month', 'tipo', 'Line Of Business'], as_index=False)['value'].sum()
df_data_agg.sort_values(['tipo', 'Line Of Business', 'ordenMes'], inplace=True)

# Crea una columna 'percentage' para el cálculo de variación con respecto al mes anterior LM = LastMonth
df_data_agg['percentage'] = df_data_agg.groupby(['tipo', 'Line Of Business'])['value'].pct_change() * 100

# Remplaza fill y inf a cero para graficar las variaciones y valores en cero
df_data_agg = df_data_agg.fillna(0)
df_data_agg = df_data_agg.replace([np.inf, -np.inf], 0, inplace=False)

# __________________________________________________________________
######################     DASH    ###############################
# __________________________________________________________________

## Poblacion de filtros
lineas_negocio = sorted(set(df_data_agg['Line Of Business']))
tipo = sorted(set(df_data_agg['tipo']))
percentage = ['Value', 'Variation LM']

app = dash.Dash(__name__)
 
# Estilos
filtro_style =   {
    'margin-bottom': '10px',
    'font-family': 'Poppins, sans-serif'
}

container_style = {
    'width': '80%',
    'margin': 'auto',
    'background-color': '#f9f9f9',
    'padding': '20px',
}

h1_style = {
    'text-align': 'center',
    'color': '#757575',
    'font-family': 'Poppins, sans-serif',
}
p_filter_style = {
    'text-align': 'left',
    'color': '#757575',
    'font-family': 'Poppins, sans-serif',
}
img_style = {
    'width': '200px',
    'margin': 'auto',
    'background-color': '#006699',
    'display': 'block',
    'border-radius': '15px', 
}

app.layout = html.Div(
    style=container_style, 
    children=[
        html.Img(src='https://enginebi.net/wp-content/uploads/elementor/thumbs/EngineBI_Logo_Final-main-qanapc1ahka6g2op501n0wrshf8f79sqg4p8pewmug.png', style=img_style),
        html.H1("Comparison of Revenue and Service Costs", style=h1_style),

        # Filtro para Tipo (Revenue o Cost)
        html.P("Select Revenue/Cost:", style=p_filter_style),
        dcc.Dropdown(
            id='tipo-dropdown',
            options=[
                {'label': t, 'value': t} for t in tipo
            ],
            multi=True,
            value=tipo,
            style=filtro_style
        ),

        # Filtro para Líneas de Negocio
        html.P("Line Of Business:", style=p_filter_style),
        dcc.Dropdown(
            id='lineas-negocio-dropdown',
            options=[
                {'label': linea, 'value': linea} for linea in lineas_negocio
            ],
            multi=True,
            value=lineas_negocio,
            style=filtro_style
        ),

        #
        # Filtro para percentage o Value
        html.P("Compare evolution as:", style=p_filter_style),
        dcc.Dropdown(
            id='percentage-dropdown',
            options=[
                {'label': p, 'value': p} for p in percentage
            ],
            multi=False,
            value='Value',
            style=filtro_style
        ),

        
        dcc.Graph(
            id='evolucion-grafica',
            config={'displayModeBar': False}
        ),
    ] 
    )


@app.callback(
    Output('evolucion-grafica', 'figure'),
    [Input('lineas-negocio-dropdown', 'value'),
     Input('tipo-dropdown', 'value'),
     Input('percentage-dropdown', 'value')]
)
def update_graph(selected_lineas_negocio, selected_tipo, selected_percentage):
    # Filtrar datos según la selección del usuario
    df_filtrado = df_data_agg[(df_data_agg['Line Of Business'].isin(selected_lineas_negocio)) &
                              (df_data_agg['tipo'].isin(selected_tipo))]
 
    traces = []
    for linea in selected_lineas_negocio:
        for t in selected_tipo:
            df_temp = df_filtrado[(df_filtrado['Line Of Business'] == linea) & (df_filtrado['tipo'] == t)]
            if selected_percentage == 'Value':
                y_values = df_temp['value']
                y_title = 'Value (Revenue)' if t == 'Revenue' else 'Value (Cost)'
            else:
                y_values = df_temp['percentage']
                y_title = 'Percentage change (Revenue)' if t == 'Revenue' else 'Percentage change (Cost)'

            trace = go.Scatter(
                x=df_temp['month'],
                y=y_values,
                mode='lines+markers',
                name=f'{t} - {linea}',
                hoverinfo='text',
                text=[f'Month: {mes}<br>Value: ${valor:,.2f}<br>% Variation LM: {percentage:.2f}%<br>Line Of Business: {linea}<br>{t}'
      for mes, valor, percentage, t in
      zip(df_temp['month'], df_temp['value'], df_temp['percentage'], df_temp['tipo'])]
,
                yaxis='y2' if t == 'Cost' else 'y', 
                line={'width': 3, 'dash': 'dot'} if t == 'Cost' else {'width': 3} 
            )
            traces.append(trace)


    layout = {
        'title': 'Evolution of Income and Costs',
        'xaxis': {'title': 'Month', 'font': {'family': 'Poppins, sans-serif'}},
        'yaxis': {'title': y_title, 'rangemode': 'tozero', 'fixedrange': True},
        'yaxis2': {'title': 'Value (Costo)', 'rangemode': 'tozero', 'overlaying': 'y', 'side': 'right', 'fixedrange': True},
        'legend': {'title': 'Línea de Negocio'},
        'showlegend': True,
        'margin': {'l': 40, 'b': 40, 't': 60, 'r': 10},
        'yaxis2_tickformat': '$,.2f',
    }

    return {'data': traces, 'layout': layout}


if __name__ == '__main__':
    app.run_server(debug=True)
