import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import Dash, html, Input, Output, State, callback_context
import copy

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Se crea el layout de la aplicacion web
app.layout = html.Div([
    dbc.Button("Agregar Nodo", id="open-node-modal", n_clicks=0, className="m-2"),
    dbc.Button("Agregar Arista", id="open-edge-modal", n_clicks=0, className="m-2"),
    dbc.Button("Guardar Grafo", id="open-save-modal", n_clicks=0, className="m-2"),
    dbc.Button("Deshacer", id="undo-button", n_clicks=0, className="m-2"),
    cyto.Cytoscape(
        id='cytoscape',
        layout={'name': 'circle'},
        style={'width': '100%', 'height': '450px'},
        elements=[]
    ),
    dbc.Modal([
        dbc.ModalHeader("Agregar Nodo"),
        dbc.ModalBody([
            dbc.Input(id='node-id-input', placeholder='ID Nodo', type='text', className="mb-2"),
            dbc.Input(id='node-label-input', placeholder='Etiqueta Nodo', type='text', className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Agregar", id="add-node-button", n_clicks=0, className="ml-auto"),
            dbc.Button("Cerrar", id="close-node-modal", className="ml-auto")
        ])
    ], id="node-modal", is_open=False),
    dbc.Modal([
        dbc.ModalHeader("Agregar Arista"),
        dbc.ModalBody([
            dbc.Input(id='edge-source-input', placeholder='ID Nodo Inicio', type='text', className="mb-2"),
            dbc.Input(id='edge-target-input', placeholder='ID Nodo Fin', type='text', className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Agregar", id="add-edge-button", n_clicks=0, className="ml-auto"),
            dbc.Button("Cerrar", id="close-edge-modal", className="ml-auto")
        ])
    ], id="edge-modal", is_open=False),
    dbc.Modal([
        dbc.ModalHeader("Guardar Grafo"),
        dbc.ModalBody([
            dbc.Input(id='filename-input', placeholder='Nombre del archivo', type='text', className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Guardar", id="save-graphml-button", n_clicks=0, className="ml-auto"),
            dbc.Button("Cerrar", id="close-save-modal", className="ml-auto")
        ])
    ], id="save-modal", is_open=False),
])

# Se crea una lista para guardar el estado del grafo en cada momento que se haga un cambio
historial = []


# Se abre el modal para agregar nodo
@app.callback(
    Output("node-modal", "is_open"),
    [Input("open-node-modal", "n_clicks"), Input("close-node-modal", "n_clicks"), Input("add-node-button", "n_clicks")],
    [State("node-modal", "is_open")]
)
def toggle_node_modal(open_click, close_click, add_click, is_open):
    ctx = callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "add-node-button" and open_click > 0:
            return False  # se cierra el modal luego de agregar el nodo
        if button_id in ["open-node-modal", "close-node-modal"]:
            return not is_open
    return is_open


# Se abre el modal para agregar aristas
@app.callback(
    Output("edge-modal", "is_open"),
    [Input("open-edge-modal", "n_clicks"), Input("close-edge-modal", "n_clicks"), Input("add-edge-button", "n_clicks")],
    [State("edge-modal", "is_open")]
)
def toggle_edge_modal(open_click, close_click, add_click, is_open):
    ctx = callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "add-edge-button" and open_click > 0:
            return False  # Se cierra el modal leugo de agregar arista
        if button_id in ["open-edge-modal", "close-edge-modal"]:
            return not is_open
    return is_open


# Se abre el modal para guardar el grafo
@app.callback(
    Output("save-modal", "is_open"),
    [Input("open-save-modal", "n_clicks"), Input("close-save-modal", "n_clicks"),
     Input("save-graphml-button", "n_clicks")],
    [State("save-modal", "is_open")]
)
def toggle_save_modal(open_click, close_click, save_click, is_open):
    ctx = callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id in ["open-save-modal", "close-save-modal"]:
            return not is_open
    return is_open


# Se actualiza el grafo en la aplicacion web
@app.callback(
    Output("cytoscape", "elements"),
    [Input("add-node-button", "n_clicks"), Input("add-edge-button", "n_clicks"), Input('cytoscape', 'tapNode'),
     Input("undo-button", "n_clicks")],
    [State("cytoscape", "elements"),
     State("node-id-input", "value"),
     State("node-label-input", "value"),
     State("edge-source-input", "value"),
     State("edge-target-input", "value")]
)
def update_elements(node_clicks, edge_clicks, tap_node, undo_clicks, elements, node_id, node_label, edge_source,
                    edge_target):
    ctx = callback_context
    if not ctx.triggered:
        return elements

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id != "undo-button":
        historial.append(copy.deepcopy(elements))  # Se guarda el estado actual en el historial

    if button_id == "add-node-button" and node_id and node_label:
        new_node = {"data": {"id": node_id, "label": node_label}}
        elements.append(new_node)

    if button_id == "add-edge-button" and edge_source and edge_target:
        new_edge = {"data": {"source": edge_source, "target": edge_target}}
        elements.append(new_edge)

    if button_id == 'cytoscape' and tap_node:
        node_id_to_remove = tap_node['data']['id']
        elements = [ele for ele in elements if ele['data'].get('id') != node_id_to_remove and
                    ele['data'].get('source') != node_id_to_remove and ele['data'].get('target') != node_id_to_remove]

    if button_id == "undo-button" and historial:
        elements = historial.pop()  # Se restaura el ultimo estado guardado en el historial

    return elements


# Se limpian los inputs de los modales
@app.callback(
    [Output("node-id-input", "value"),
     Output("node-label-input", "value"),
     Output("edge-source-input", "value"),
     Output("edge-target-input", "value"),
     Output("filename-input", "value")],
    [Input("add-node-button", "n_clicks"),
     Input("add-edge-button", "n_clicks"),
     Input("save-graphml-button", "n_clicks")]
)
def clear_inputs(add_node_clicks, add_edge_clicks, save_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return ["", "", "", "", ""]

    return ["", "", "", "", ""]


# Se crea un grafo de networkx a partir de los elementos del grafo en la aplicacion web
@app.callback(
    Output("save-graphml-button", "n_clicks"),
    [Input("save-graphml-button", "n_clicks")],
    [State("cytoscape", "elements"), State("filename-input", "value")]
)
def save_graphml_button_click(n_clicks, elements, filename):
    if n_clicks > 0 and filename:
        G = nx.Graph()
        for element in elements:
            if "source" in element["data"]:
                G.add_edge(element["data"]["source"], element["data"]["target"])
            else:
                G.add_node(element["data"]["id"], label=element["data"]["label"])
        nx.write_graphml(G, filename + ".graphml")
    return 0


# Se ejecuta la aplicacion web
if __name__ == "__main__":
    app.run_server(debug=True)
