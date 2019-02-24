# encoding=utf-8
from pathlib import Path
import os
from bottle import route, view, run, request, post, template
import network_construction.network as nc
import network_construction.database as db
from network_analysis import network
from data_platform.config import ConfigManager
from data_platform.datasource.networkx import NetworkXDS


@route('/load')
def analysis():
    return template('loadgraph')


@route('/analysis', method='get')
@view('analysis')
def do_analysis():
    gname = request.query.graphname
    gtype = request.query.graphtype
    net_type = request.query.nettype
    weight_type = request.query.weighttype
    g = network.Net(gname, net_type, weight_type)
    if gtype == 'component':
        g = g.extract_max_component()
    elif gtype == 'ego':
        core = request.query.ego_core
        radius = int(request.query.ego_radius)
        g = g.extract_ego_network(core, radius)
    elif gtype == 'community':
        g = g.extract_louvain_communities()
    data = {'graphname': gname,
            'graphtype': gtype,
            'g': g}
    return data


@route('/construction')
@view('construction')
def do_construction():
    graphtype = request.query.graphtype
    print(graphtype)
    data = {'graphtype': graphtype, }
    print(data)
    return data


@post('/text')
@view('create')
def do_text():
    database = request.forms.get('database')
    print(database)
    db.create_database(database)
    db.flush()
    source = request.forms.get('source')
    document = request.forms.get('document')
    node = request.forms.get('node')
    relation = request.forms.get('relation')
    nc.create_network_text(source, document, node, relation, database)
    db.flush()

    current_location = Path(os.getcwd())
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        },
        "file_format": "graphml"
    })
    print(graph_location)
    nxds = NetworkXDS(config)  # 读取网络用模块
    print(nxds.read_graph())
    network0 = nxds.read_graph(database)[database]
    scale = network0.number_of_nodes()
    size = network0.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database + '.graphml',
            'source': source,
            'document': document,
            'node': node,
            'relation': relation,
            'node_number': scale,
            'edge_number': size,
            'nettype': node + ' ' + 'word network',
            'weighttype': 'count'}
    print(data)
    return data


@post('/author')
@view('create')
def do_author():
    database = request.forms.get('database')
    print(database)
    db.flush()
    db.create_database(database)
    source = request.forms.get('source')
    document = request.forms.get('document')
    relation = request.forms.get('relation')
    nc.create_network_author(source, document, relation, database)
    db.flush()
    current_location = Path(os.getcwd())
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        },
        "file_format": "graphml"
    })
    print(graph_location)
    nxds = NetworkXDS(config)  # 读取网络用模块
    print(nxds.read_graph())
    network0 = nxds.read_graph(database)[database]
    scale = network0.number_of_nodes()
    size = network0.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database + '.graphml',
            'source': source,
            'document': document,
            'node': "undefined",
            'relation': relation,
            'node_number': scale,
            'edge_number': size,
            'nettype': 'author citation network',
            'weighttype': 'cite_count'}
    #nettype可以为co work network，此时weighttype改为co_count,这个要在后续版本中再进行动态的修改，暂时只使用citation即可。
    print(data)
    return data


@post('/paper')
@view('create')
def do_paper():
    database = request.forms.get('database')
    print(database)
    db.flush()
    db.create_database(database)
    source = request.forms.get('source')
    document = request.forms.get('document')
    relation = request.forms.get('relation')
    nc.create_network_paper(source, document, relation, database)
    db.flush()
    current_location = Path(os.getcwd())
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        },
        "file_format": "graphml"
    })
    print(graph_location)
    nxds = NetworkXDS(config)  # 读取网络用模块
    print(nxds.read_graph())
    network0 = nxds.read_graph(database)[database]
    scale = network0.number_of_nodes()
    size = network0.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database + '.graphml',
            'source': source,
            'document': document,
            'node': "undefined",
            'relation': relation,
            'node_number': scale,
            'edge_number': size,
            'nettype': 'paper citation network',
            'weighttype': 'cite_count'}
    print(data)
    return data


@post('/other')
@view('create')
def do_other():
    database = request.forms.get('database')
    print(database)
    db.flush()
    db.create_database(database)
    source = request.forms.get('source')
    document = request.forms.get('document')
    relation = request.forms.get('relation')
    nc.create_other(source, document, relation, database)
    db.flush()
    current_location = Path(os.getcwd())
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        },
        "file_format": "graphml"
    })
    print(graph_location)
    nxds = NetworkXDS(config)  # 读取网络用模块
    print(nxds.read_graph())
    network0 = nxds.read_graph(database)[database]
    scale = network0.number_of_nodes()
    size = network0.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database + '.graphml',
            'source': source,
            'document': document,
            'node': "undefined",
            'relation': relation,
            'node_number': scale,
            'edge_number': size,
            'nettype': 'paper author or paper word network',
            'weighttype': 'relation_count'}
    print(data)
    return data


run(host='localhost', port=8080, reloader=True, debug=True)
