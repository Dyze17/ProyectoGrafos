import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
from dash import Dash, html, Input, Output, State, callback_context
import copy

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Button("Agregar Nodo", id="open-node-modal", n_clicks=0, className="m-2"),
    dbc.Button("Agregar Arista", id="open-edge-modal", n_clicks=0, className="m-2"),
    dbc.Button("Guardar Grafo", id="open-save-modal", n_clicks=0, className="m-2"),
    dbc.Button("Deshacer", id="undo-button", n_clicks=0, className="m-2"),
    dbc.Button("Camino Más Corto", id="open-shortest-path-modal", n_clicks=0, className="m-2"),
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
    dbc.Modal([
        dbc.ModalHeader("Camino Más Corto"),
        dbc.ModalBody([
            dbc.Input(id='path-source-input', placeholder='ID Nodo Inicio', type='text', className="mb-2"),
            dbc.Input(id='path-target-input', placeholder='ID Nodo Fin', type='text', className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Encontrar Camino", id="find-shortest-path-button", n_clicks=0, className="ml-auto"),
            dbc.Button("Cerrar", id="close-shortest-path-modal", className="ml-auto")
        ])
    ], id="shortest-path-modal", is_open=False),
    html.Div(id='error-message', style={'color': 'red', 'margin-top': '10px'})  # Div para mostrar mensajes de error
])

# Mantener historial de estados del grafo
history = []


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
            return False  # Se cierra el modal luego de agregar arista
        if button_id in ["open-edge-modal", "close-edge-modal"]:
            return not is_open
    return is_open


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


@app.callback(
    Output("shortest-path-modal", "is_open"),
    [Input("open-shortest-path-modal", "n_clicks"), Input("close-shortest-path-modal", "n_clicks"),
     Input("find-shortest-path-button", "n_clicks")],
    [State("shortest-path-modal", "is_open")]
)
def toggle_shortest_path_modal(open_click, close_click, find_click, is_open):
    ctx = callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "find-shortest-path-button" and open_click > 0:
            return False  # se cierra el modal luego de encontrar el camino más corto
        if button_id in ["open-shortest-path-modal", "close-shortest-path-modal"]:
            return not is_open
    return is_open


@app.callback(
    Output("cytoscape", "elements"),
    Output('error-message', 'children'),
    [Input("add-node-button", "n_clicks"), Input("add-edge-button", "n_clicks"), Input('cytoscape', 'tapNode'),
     Input("undo-button", "n_clicks"), Input("find-shortest-path-button", "n_clicks")],
    [State("cytoscape", "elements"),
     State("node-id-input", "value"),
     State("node-label-input", "value"),
     State("edge-source-input", "value"),
     State("edge-target-input", "value"),
     State("path-source-input", "value"),
     State("path-target-input", "value")]
)
def update_elements(node_clicks, edge_clicks, tap_node, undo_clicks, find_path_clicks, elements, node_id, node_label,
                    edge_source, edge_target, path_source, path_target):
    ctx = callback_context
    if not ctx.triggered:
        return elements, ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id != "undo-button":
        history.append(copy.deepcopy(elements))  # Guardar el estado actual en el historial

    if button_id == "add-node-button":
        if node_id and node_label:
            for ele in elements:
                if ele['data'].get('id') == node_id:
                    return elements, "Error: Ya existe un nodo con el ID proporcionado."
            new_node = {"data": {"id": node_id, "label": node_label}}
            elements.append(new_node)
        else:
            return elements, "Error: ID y etiqueta del nodo son obligatorios."

    if button_id == "add-edge-button":
        if edge_source and edge_target:
            node_ids = [ele['data'].get('id') for ele in elements if 'id' in ele['data']]
            if edge_source not in node_ids or edge_target not in node_ids:
                return elements, "Error: Ambos nodos deben existir para crear una arista."
            new_edge = {"data": {"source": edge_source, "target": edge_target}}
            elements.append(new_edge)
        else:
            return elements, "Error: IDs de nodo de inicio y fin son obligatorios."

    if button_id == 'cytoscape' and tap_node:
        node_id_to_remove = tap_node['data']['id']
        elements = [ele for ele in elements if ele['data'].get('id') != node_id_to_remove and
                    ele['data'].get('source') != node_id_to_remove and ele['data'].get('target') != node_id_to_remove]

    if button_id == "undo-button" and history:
        elements = history.pop()  # Restaurar el último estado del historial

    if button_id == "find-shortest-path-button":
        if path_source and path_target:
            G = nx.Graph()
            for element in elements:
                if "source" in element["data"]:
                    G.add_edge(element["data"]["source"], element["data"]["target"])
                else:
                    G.add_node(element["data"]["id"])
            if path_source not in G or path_target not in G:
                return elements, "Error: Ambos nodos deben existir en el grafo."
            try:
                shortest_path = nx.shortest_path(G, source=path_source, target=path_target)
                for ele in elements:
                    if 'source' in ele['data'] and 'target' in ele['data']:
                        if (ele['data']['source'] in shortest_path and ele['data']['target'] in shortest_path and
                                abs(shortest_path.index(ele['data']['source']) - shortest_path.index(
                                    ele['data']['target'])) == 1):
                            ele['classes'] = 'highlighted'
                        else:
                            ele.pop('classes', None)
                    elif ele['data']['id'] in shortest_path:
                        ele['classes'] = 'highlighted'
                    else:
                        ele.pop('classes', None)
            except nx.NetworkXNoPath:
                return elements, "Error: No hay camino entre los nodos proporcionados."
        else:
            return elements, "Error: IDs de nodo de inicio y fin son obligatorios."

    return elements, ""


@app.callback(
    [Output("node-id-input", "value"),
     Output("node-label-input", "value"),
     Output("edge-source-input", "value"),
     Output("edge-target-input", "value"),
     Output("filename-input", "value"),
     Output("path-source-input", "value"),
     Output("path-target-input", "value")],
    [Input("add-node-button", "n_clicks"),
     Input("add-edge-button", "n_clicks"),
     Input("save-graphml-button", "n_clicks"),
     Input("find-shortest-path-button", "n_clicks")]
)
def clear_inputs(add_node_clicks, add_edge_clicks, save_clicks, find_path_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return ["", "", "", "", "", "", ""]

    return ["", "", "", "", "", "", ""]


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


if __name__ == "__main__":
    app.run_server(debug=True)
