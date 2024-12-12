import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import copy
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#app = dash.Dash(__name__)
app.title = "SEM Tabanlı Yöntemle Yol Analizi"
server = app.server

# Başlangıç graf (SEM benzeri, katsayılar "yapısal ilişkiler")
initial_nodes = ['A', 'B', 'C', 'D', 'E']
initial_edges = [
    ('A', 'B', 2),
    ('A', 'C', 4),
    ('B', 'C', 1),
    ('B', 'D', 7),
    ('C', 'D', 3),
    ('C', 'E', 5),
    ('D', 'E', 1),
]

default_source = 'A'
default_target = 'E'

def run_sem_model(nodes, edges, start, end):
    # Burada SEM benzeri bir yaklaşım gösteriyoruz:
    # Buradaki "mesafeler" aslında "uyumluluk skorları" olarak varsayılsın.
    # Dijkstra benzeri mantık: düşük skor = yüksek uyum (ters mantık yapıyoruz).
    # Gerçekte SEM böyle çalışmaz ama istenen konsepte yaklaşmak için benzetim yapıyoruz.
    
    # Burada da mesafeler yerine "maliyet" benzeri bir şey kullanıyoruz, 
    # ancak bunu "uyumsuzluk" gibi düşünebiliriz.
    
    
    distances = {n: float('inf') for n in nodes}
    visited = {n: False for n in nodes}
    previous = {n: None for n in nodes}

    # SEM'de her kenarı yapısal bir ilişki olarak göreceğiz. 
    # Burada düşük ağırlık = yüksek uyum diye varsayıyoruz.
    distances[start] = 0

    # adjacency list
    adj = {n: [] for n in nodes}
    for (s, t, w) in edges:
        adj[s].append((t, w))
        adj[t].append((s, w))

    steps = []

    for i in range(len(nodes)):
        u = None
        for node in nodes:
            if not visited[node] and (u is None or distances[node] < distances[u]):
                u = node

        if u is None or distances[u] == float('inf'):
            break

        visited[u] = True

        step_detail = {
            'current': u,
            'distances': copy.deepcopy(distances),
            'visited': copy.deepcopy(visited),
            'checks': []
        }

        # Her komşu yapısal ilişkiyi kontrol et
        for (v, w) in adj[u]:
            # if v == start:  # Başlangıç düğümüne geri dönüşü atla
            #     continue
            
            old_dist = distances[v]
            old_dist_display = "∞" if old_dist == float('inf') else old_dist  # Sonsuzluğu gösterim için dönüştür
            alt = distances[u] + w
            updated = False
            if alt < distances[v]:
                distances[v] = alt
                previous[v] = u
                updated = True

            # Başlangıç düğümüne dönüşlerde eski ve yeni değerleri doğru şekilde göster
            if v == start:
                alt_display = alt  # Yeni uyumsuzluk alt değeri olur
            else:
                alt_display = distances[v]


            step_detail['checks'].append({
                'from': u,
                'to': v,
                'old_dist': old_dist_display,
                'new_dist': alt_display,
                'weight': w,
                'updated': updated
            })

        steps.append(step_detail)

    path = []
    curr = end
    while previous[curr] is not None:
        path.append(curr)
        curr = previous[curr]
    if curr == start:
        path.append(start)
    path.reverse()

    return steps, path

def node_position(n):
    positions = {
        'A': (100, 100),
        'B': (200, 100),
        'C': (300, 200),
        'D': (200, 300),
        'E': (100, 300)
    }
    if n in positions:
        x, y = positions[n]
    else:
        import random
        x, y = random.randint(50,350), random.randint(50,350)
    return {'x': x, 'y': y}





# def generate_elements(nodes, edges, source, target, step_info=None, path=[]):
#     visited = {}
#     if step_info:
#         visited = step_info.get('visited', {})

#     # Node renk ayarları
#     node_colors = {
#         'source': '#4ade80',  # Başlangıç düğümü: Yeşil
#         'target': '#f87171',  # Hedef düğümü: Kırmızı
#         'visited': '#fbbf24',  # Ziyaret edilen düğüm: Sarı
#         'normal': '#60a5fa'   # Normal düğüm: Mavi
#     }

#     elems = []

#     # Düğüm ekleme
#     for n in nodes:
#         color = node_colors['normal']
#         if n == source:
#             color = node_colors['source']
#         elif n == target:
#             color = node_colors['target']
#         elif visited.get(n):
#             color = node_colors['visited']

#         elems.append({
#             'data': {'id': n, 'label': n},
#             'style': {
#                 'background-color': color,
#                 'color': '#ffffff'
#             },
#             'position': node_position(n)  # Düğüm pozisyonları
#         })

#     # Path içindeki kenarları kırmızı yapmak için bir set oluştur
#     edges_in_path = set()
#     for i in range(len(path) - 1):
#         s, t = path[i], path[i + 1]
#         edges_in_path.add((s, t))  # S -> T yönü
#         edges_in_path.add((t, s))  # T -> S yönü (çift yönlü graf için)

#     # Kenar ekleme
#     for (s, t, w) in edges:
#         style = {
#             'line-color': '#ccc',  # Varsayılan gri renk
#             'width': 2             # Varsayılan genişlik
#         }
#         # Eğer kenar path içindeyse kırmızı yap
#         if (s, t) in edges_in_path or (t, s) in edges_in_path:
#             style = {
#                 'line-color': '#ef4444',  # Kırmızı renk
#                 'width': 5,               # Daha kalın çizgi
#                 'target-arrow-color': '#ef4444'  # Kırmızı ok
#             }

#         elems.append({
#             'data': {
#                 'id': f'{s}-{t}',
#                 'source': s,
#                 'target': t,
#                 'weight': w
#             },
#             'style': style
#         })

#     return elems


def generate_elements(nodes, edges, source, target, step_info=None, path=[]):
    visited = {}
    if step_info:
        visited = step_info.get('visited', {})

    # Node renk ayarları
    node_colors = {
        'source': '#4ade80',  # Başlangıç düğümü: Yeşil
        'target': '#f87171',  # Hedef düğümü: Kırmızı
        'visited': '#fbbf24',  # Ziyaret edilen düğüm: Sarı
        'normal': '#60a5fa'   # Normal düğüm: Mavi
    }

    elems = []

    # Düğüm ekleme
    for n in nodes:
        color = node_colors['normal']
        if n == source:
            color = node_colors['source']
        elif n == target:
            color = node_colors['target']
        elif visited.get(n):
            color = node_colors['visited']

        elems.append({
            'data': {'id': n, 'label': n},
            'style': {
                'background-color': color,
                'color': '#ffffff'
            },
            'position': node_position(n)  # Düğüm pozisyonları
        })

    # Path içindeki kenarları kırmızı yapmak için bir set oluştur
    edges_in_path = set()
    for i in range(len(path) - 1):
        s, t = path[i], path[i + 1]
        edges_in_path.add((s, t))  # S -> T yönü
        edges_in_path.add((t, s))  # T -> S yönü (çift yönlü graf için)

    # Kenar ekleme
    for (s, t, w) in edges:
        style = {
            'line-color': '#ccc',  # Varsayılan gri renk
            'width': 2             # Varsayılan genişlik
        }
        # Eğer kenar path içindeyse kırmızı yap
        if (s, t) in edges_in_path or (t, s) in edges_in_path:
            style = {
                'line-color': '#ef4444',  # Kırmızı renk
                'width': 5,               # Daha kalın çizgi
                'target-arrow-color': '#ef4444'  # Kırmızı ok
            }

        elems.append({
            'data': {
                'id': f'{s}-{t}',
                'source': s,
                'target': t,
                'weight': w
            },
            'style': style
        })

    
    return elems



def format_step_info(step_index, steps, path,edges):
    if step_index < 0:
        return "SEM tabanlı analizi başlatın."
    step = steps[step_index]
    info_lines = []
    info_lines.append(f"Adım {step_index+1}/{len(steps)}:")
    info_lines.append(f"İşlenen değişken (düğüm): {step['current']}")
    if step['checks']:
        info_lines.append("İncelenen yapısal ilişkiler ve güncellenen uyum skorları:")
        for ch in step['checks']:
            line = f"- {ch['from']} -> {ch['to']} (İlişki katsayısı={ch['weight']}): eski uyumsuzluk={ch['old_dist']}, yeni uyumsuzluk={ch['new_dist']}"
            
            if ch['updated']:
                line += " [GÜNCELLENDİ]"
            info_lines.append(line)
    else:
        info_lines.append("Bu adımda incelenecek yapısal ilişki yok.")

    # Son adımda en uyumlu yol bulunduysa göster
    if step_index == len(steps)-1 and len(path) > 0:
        info_lines.append("")
        info_lines.append("En uyumlu yapısal yol bulundu: " + " -> ".join(path))
        total_cost = 0
        for i in range(len(path)-1):
            s = path[i]
            t = path[i+1]
            for (x, y, w) in edges:
                if (x == s and y == t) or (x == t and y == s):
                    total_cost += w
                    break
        info_lines.append(f"Toplam Yapısal Uyumsuzluk Skoru: {total_cost} (Daha düşük daha iyi)")

    return "\n".join(info_lines)

stylesheet = [
    {
        'selector': 'node',
        'style': {
            'width': '40px',
            'height': '40px',
            'label': 'data(label)',
            'text-halign': 'center',
            'text-valign': 'center',
            'font-weight': 'bold',
            'font-size': '12px',
            'border-color': '#000',
            'border-width': 2
        }
    },
    {
        'selector': 'edge',
        'style': {
            'width': 3,
            # 'line-color': '#ccc',
            'curve-style': 'bezier',          # Kıvrımlı stil
            'label': 'data(weight)',
            'font-size': '12px',
            'text-background-opacity': 1,
            'text-background-color': '#fff',
            'text-background-padding': '2px',
            'text-rotation': 'autorotate',
            'color': '#333',
            'target-arrow-shape': 'none',    # Okları kaldır
            'source-arrow-shape': 'none'     # Çift yönlü düz çizgi
        }
    }
]



app.layout = html.Div(style={'display':'flex','flexDirection':'column','minHeight':'100vh','background':'#f9fafb'},
    children=[
        dbc.Toast(
            id="result-toast",
            header="Sonuç",
            is_open=False,
            dismissable=True,
            icon="success",
            style={"position": "fixed", "top": 100, "right": 100, "width": 900, "maxWidth": "90vw","zIndex": 1050, "backgroundColor": "#4ade80","boxShadow": "0 4px 6px rgba(0,0,0,0.1)"},
        ),

        html.Header(style={'background':'white','padding':'20px','boxShadow':'0 2px 4px rgba(0,0,0,0.1)'},
            children=[
                html.H1("SEM Tabanlı Yapısal Yol Analizi",style={'textAlign':'center','margin':0})
            ]
        ),
        html.Div(style={'flex':'1','display':'flex','flexWrap':'wrap','padding':'20px','gap':'20px'},
            children=[
                html.Div(
                    style={'flex':'1','minWidth':'250px','background':'white','padding':'20px','borderRadius':'8px','boxShadow':'0 2px 4px rgba(0,0,0,0.1)'},
                    children=[
                        html.H2("Graf Düzenleme Paneli", style={'marginBottom':'10px'}),

                        html.H3("Düğüm Ekle / Sil"),
                        dcc.Input(id='node-add-input', placeholder='Düğüm adı', type='text', style={'marginRight':'10px'}),
                        html.Button("Ekle", id="node-add-button", style={'marginRight':'10px','marginTop':'5px','backgroundColor':'#4ade80','border':'none','color':'white','padding':'5px 10px','borderRadius':'4px'}),
                        dcc.Dropdown(id='node-remove-dropdown', placeholder='Silinecek düğüm', style={'width':'150px','display':'inline-block','marginTop':'5px'}),
                        html.Button("Sil", id="node-remove-button", style={'marginLeft':'10px','backgroundColor':'#dc2626','border':'none','color':'white','padding':'5px 10px','borderRadius':'4px'}),

                        html.H3("Kenar (Yapısal İlişki) Ekle / Sil", style={'marginTop':'20px'}),
                        html.Div([
                            dcc.Input(id='edge-add-input-source', placeholder='Kaynak değişken', type='text', style={'marginRight':'5px','width':'100px'}),
                            dcc.Input(id='edge-add-input-target', placeholder='Hedef değişken', type='text', style={'marginRight':'5px','width':'100px'}),
                            dcc.Input(id='edge-add-input-weight', placeholder='İlişki Ağırlığı', type='number', style={'marginRight':'10px','width':'80px'}),
                            html.Button("Ekle", id="edge-add-button", style={'marginTop':'5px','backgroundColor':'#4ade80','border':'none','color':'white','padding':'5px 10px','borderRadius':'4px'})
                        ], style={'marginBottom':'10px'}),
                        dcc.Dropdown(id='edge-remove-dropdown', placeholder='Silinecek ilişki', style={'width':'200px','display':'inline-block'}),
                        html.Button("Sil", id="edge-remove-button", style={'marginLeft':'10px','backgroundColor':'#dc2626','border':'none','color':'white','padding':'5px 10px','borderRadius':'4px'}),

                        html.H3("Başlangıç ve Hedef Değişken Seçimi", style={'marginTop':'20px'}),
                        dcc.Dropdown(id='start-node-dropdown', placeholder='Başlangıç değişkeni seçin', value=default_source, style={'marginBottom':'10px'}),
                        dcc.Dropdown(id='end-node-dropdown', placeholder='Hedef değişkeni seçin', value=default_target),

                        html.H3("Açıklama", style={'marginTop':'20px'}),
                        html.P("Bu örnekte Yapısal Eşitlik Modellemesi (SEM) kavramından esinlenerek bir yol analizi yapılmaktadır."),
                        html.P("Sol panelden değişken/ilişki ekleyip çıkarın, başlangıç/hedef değişkenleri seçin. Graf üzerine tıklayarak da başlangıç/hedef belirleyebilirsiniz. 'Başlat', 'Sonraki Adım', 'Önceki Adım' ve 'Sıfırla' butonlarıyla süreci takip edin."),
                    ]
                ),

                html.Div(
                    style={'flex':'2','minWidth':'400px','background':'white','padding':'20px','borderRadius':'8px','boxShadow':'0 2px 4px rgba(0,0,0,0.1)','display':'flex','flexDirection':'column','alignItems':'center'},
                    children=[
                        html.H2("SEM Tabanlı Yol Görselleştirmesi", style={'marginBottom':'10px'}),
                        html.Div(id='current-nodes', style={'fontWeight':'bold','marginBottom':'10px'}),
                        cyto.Cytoscape(
                            id='cytoscape-graph',
                            elements=[],
                            layout={'name': 'preset'},
                            style={'width': '500px', 'height': '400px','border':'1px solid #ccc','borderRadius':'4px'},
                            stylesheet=stylesheet
                        ),
                        html.Pre(id='info', style={'marginTop':'10px','color':'#555','minHeight':'200px','whiteSpace':'pre-wrap','background':'#f0f0f0','padding':'10px','borderRadius':'4px','border':'1px solid #ccc'}),
                        html.Div(style={'marginTop':'20px','display':'flex','gap':'10px','justifyContent':'center'}, children=[
                            html.Button("Başlat", id="start-button", n_clicks=0, style={'padding':'10px 20px','backgroundColor':'#2563eb','color':'white','borderRadius':'4px','border':'none','cursor':'pointer'}),
                            html.Button("Önceki Adım", id="prev-step-button", n_clicks=0, style={ 'padding': '10px 20px', 'backgroundColor': '#facc15', 'color': 'black', 'borderRadius': '4px', 'border': 'none', 'cursor': 'pointer' }),
                            html.Button("Sonraki Adım", id="step-button", n_clicks=0, style={'padding':'10px 20px','backgroundColor':'#16a34a','color':'white','borderRadius':'4px','border':'none','cursor':'pointer'}),
                            html.Button("Sıfırla", id="reset-button", n_clicks=0, style={'padding':'10px 20px','backgroundColor':'#dc2626','color':'white','borderRadius':'4px','border':'none','cursor':'pointer'}),
                        ])
                    ]
                )
            ]
        ),
        html.Footer(
            style={'textAlign':'center','padding':'10px','background':'white','fontSize':'12px','color':'#666','borderTop':'1px solid #eee'},
            children="© 2024 Örnek Proje"
        ),

        dcc.Store(id='graph-data', data={
            'nodes': initial_nodes, 
            'edges': initial_edges, 
            'source': default_source, 
            'target': default_target, 
            'steps':[], 
            'path':[], 
            'current_step':-1, 
            'is_running':False
        })
    ]
)

@app.callback(
    Output('graph-data', 'data'),
    Output('node-remove-dropdown', 'options'),
    Output('edge-remove-dropdown', 'options'),
    Output('start-node-dropdown', 'options'),
    Output('end-node-dropdown', 'options'),
    Input('node-add-button', 'n_clicks'),
    Input('node-remove-button', 'n_clicks'),
    Input('edge-add-button', 'n_clicks'),
    Input('edge-remove-button', 'n_clicks'),
    Input('start-node-dropdown', 'value'),
    Input('end-node-dropdown', 'value'),
    State('node-add-input', 'value'),
    State('node-remove-dropdown', 'value'),
    State('edge-add-input-source', 'value'),
    State('edge-add-input-target', 'value'),
    State('edge-add-input-weight', 'value'),
    State('edge-remove-dropdown', 'value'),
    State('graph-data', 'data')
)
def modify_graph(node_add, node_remove, edge_add, edge_remove,
                 start_value, end_value,
                 add_node_val, remove_node_val,
                 add_edge_source, add_edge_target, add_edge_weight,
                 remove_edge_val,
                 data):
    ctx = dash.callback_context
    nodes = data['nodes']
    edges = data['edges']

    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if trigger == 'node-add-button' and add_node_val and add_node_val not in nodes:
        nodes.append(add_node_val)
    elif trigger == 'node-remove-button' and remove_node_val and remove_node_val in nodes:
        nodes.remove(remove_node_val)
        edges = [e for e in edges if e[0]!=remove_node_val and e[1]!=remove_node_val]
        if data['source'] == remove_node_val and nodes:
            data['source'] = nodes[0]
        if data['target'] == remove_node_val and nodes:
            data['target'] = nodes[-1]
    elif trigger == 'edge-add-button' and add_edge_source and add_edge_target and add_edge_weight is not None:
        if add_edge_source in nodes and add_edge_target in nodes:
            if not any((add_edge_source == s and add_edge_target == t) or (add_edge_target == s and add_edge_source == t) for (s,t,w) in edges):
                edges.append((add_edge_source, add_edge_target, float(add_edge_weight)))
    elif trigger == 'edge-remove-button' and remove_edge_val:
        spl = remove_edge_val.split('-')
        if len(spl)==2:
            s, t = spl
            edges = [e for e in edges if not ((e[0]==s and e[1]==t) or (e[1]==s and e[0]==t))]

    data['nodes'] = nodes
    data['edges'] = edges

    if start_value in nodes:
        data['source'] = start_value
    if end_value in nodes:
        data['target'] = end_value

    node_options = [{'label': n, 'value': n} for n in nodes]
    edge_options = [{'label': f"{s}-{t}(w={w})", 'value': f"{s}-{t}"} for (s,t,w) in edges]

    return data, node_options, edge_options, node_options, node_options

@app.callback(
    Output('cytoscape-graph', 'elements'),
    Output('info', 'children'),
    Output('current-nodes', 'children'),
    Output('result-toast', 'is_open'),
    Output('result-toast', 'children'),
    Output('graph-data', 'data', allow_duplicate=True),
    Input('start-button', 'n_clicks'),
    Input('step-button', 'n_clicks'),
    Input('prev-step-button', 'n_clicks'),  # Yeni düğme için giriş
    Input('reset-button', 'n_clicks'),
    Input('cytoscape-graph', 'tapNode'),
    State('graph-data', 'data'),
    State('cytoscape-graph', 'elements'),
    prevent_initial_call=True
)
def control_buttons(start_clicks, step_clicks, prev_clicks, reset_clicks, tapNode, data, elems):
    data_out = data.copy()
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    nodes = data['nodes']
    edges = data['edges']
    source = data['source']
    target = data['target']
    steps = data['steps']
    path = data['path']
    current_step = data['current_step']
    is_running = data['is_running']

    if button_id == 'prev-step-button':
        if current_step > 0:
            current_step -= 1
            data_out['current_step'] = current_step
            step = steps[current_step]
            elems = generate_elements(nodes, edges, source, target, step_info=step, path=[])
            info_text = format_step_info(current_step, steps, path, edges)
            return elems, info_text, f"Başlangıç değişkeni: {source}, Hedef değişkeni: {target}", False, "", data_out
        else:
            return dash.no_update, "İlk adımdasınız, geri gidemezsiniz.", dash.no_update, False, "", data_out

    if button_id == 'start-button':
        if source not in nodes or target not in nodes:
            return dash.no_update, "Kaynak veya hedef değişken geçersiz.", dash.no_update, False, "", data_out
        new_steps, new_path = run_sem_model(nodes, edges, source, target)
        data_out['steps'] = new_steps
        data_out['path'] = new_path
        data_out['current_step'] = -1
        data_out['is_running'] = True
        elems = generate_elements(nodes, edges, source, target)
        info_text = "SEM analizi başlatıldı. 'Adım ilerlet' ile devam edin."
        return elems, info_text, f"Başlangıç değişkeni: {source}, Hedef değişkeni: {target}", False, "", data_out

    
    
    # elif button_id == 'step-button':
    #     if not is_running:
    #         return dash.no_update, "Analiz çalışmıyor. Önce 'Başlat' ile başlatın.", dash.no_update, False, "", data_out
    #     if current_step < len(steps)-1:
    #         current_step += 1
    #         data_out['current_step'] = current_step
    #         step = steps[current_step]
    #         final_step = (current_step == len(steps)-1)
    #         elems = generate_elements(nodes, edges, source, target, step_info=step, path=path if final_step else [])
    #         info_text = format_step_info(current_step, steps, path, edges)
    #         if final_step:
    #             result_text = [
    #                 html.P("EN UYUMLU YAPISAL YOL BULUNDU: " + " -> ".join(path), style={"fontWeight": "bold", "textTransform": "uppercase"}),
    #                 html.P(f"TOPLAM YAPISAL UYUMSUZLUK SKORU: {sum(e[2] for e in edges if (e[0], e[1]) in zip(path, path[1:]) or (e[1], e[0]) in zip(path, path[1:]))} (DAHA DÜŞÜK DAHA İYİ)", style={"fontWeight": "bold", "textTransform": "uppercase"})
    #             ]
    #             return elems, info_text, f"Başlangıç değişkeni: {source}, Hedef değişkeni: {target}", True, result_text, data_out
    #         return elems, info_text, f"Başlangıç değişkeni: {source}, Hedef değişkeni: {target}", False, "", data_out
    #     else:
    #         return dash.no_update, "Tüm adımlar tamamlandı.", dash.no_update, False, "", data_out
    elif button_id == 'step-button':
        if not is_running:
            return dash.no_update, "Analiz çalışmıyor. Önce 'Başlat' ile başlatın.", dash.no_update, False, "", data_out
        if current_step < len(steps) - 1:
            current_step += 1
            data_out['current_step'] = current_step
            step = steps[current_step]
            final_step = (current_step == len(steps) - 1)
            # Son adımda path'i gönderiyoruz
            elems = generate_elements(nodes, edges, source, target, step_info=step, path=path if final_step else [])
            info_text = format_step_info(current_step, steps, path, edges)
            if final_step:
                result_text = [
                    html.P("EN UYUMLU YAPISAL YOL BULUNDU: " + " -> ".join(path), style={"fontWeight": "bold", "textTransform": "uppercase"}),
                    html.P(f"TOPLAM YAPISAL UYUMSUZLUK SKORU: {sum(e[2] for e in edges if (e[0], e[1]) in zip(path, path[1:]) or (e[1], e[0]) in zip(path, path[1:]))} (DAHA DÜŞÜK DAHA İYİ)", style={"fontWeight": "bold", "textTransform": "uppercase"})
                ]
                return elems, info_text, f"Başlangıç değişkeni: {source}, Hedef değişkeni: {target}", True, result_text, data_out
            return elems, info_text, f"Başlangıç değişkeni: {source}, Hedef değişkeni: {target}", False, "", data_out



    elif button_id == 'reset-button':
        data_out['steps'] = []
        data_out['path'] = []
        data_out['current_step'] = -1
        data_out['is_running'] = False
        elems = generate_elements(nodes, edges, source, target)
        return elems, "Sıfırlandı. 'Başlat' ile yeniden başlayın.", f"Başlangıç değişkeni: {source}, Hedef değişkeni: {target}", False, "", data_out

    return dash.no_update, dash.no_update, dash.no_update, False, "", data_out



if __name__ == '__main__':
    app.run_server(debug=True)
