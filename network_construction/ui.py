# encoding=utf-8
from bottle import route, view, run, request, template, get, post, error, redirect
import network_construction.network as nc
import network_construction.database as db
from data_platform.config import ConfigManager
from data_platform.datasource.networkx import NetworkXDS
from pathlib import Path
import os

@route('/construction')
@view('construction')
def do_construction():
    graphtype = request.query.graphtype
    print(graphtype)
    data = {'graphtype': graphtype,}
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
    network = nxds.read_graph(database)[database]
    scale = network.number_of_nodes()
    size = network.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database,
            'source': source,
            'document': document,
            'node': node,
            'relation':relation,
            'node_number':scale,
            'edge_number':size}
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
    network = nxds.read_graph(database)[database]
    scale = network.number_of_nodes()
    size = network.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database,
            'source': source,
            'document': document,
            'node': "undefined",
            'relation': relation,
            'node_number': scale,
            'edge_number': size}
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
    network = nxds.read_graph(database)[database]
    scale = network.number_of_nodes()
    size = network.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database,
            'source': source,
            'document': document,
            'node': "undefined",
            'relation': relation,
            'node_number': scale,
            'edge_number': size}
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
    network = nxds.read_graph(database)[database]
    scale = network.number_of_nodes()
    size = network.number_of_edges()
    print(scale)
    print(size)
    data = {'database': database,
            'source': source,
            'document': document,
            'node': "undefined",
            'relation': relation,
            'node_number': scale,
            'edge_number': size}
    print(data)
    return data


@error(404)
def error404(error):
    return '请访问正确的地址，URL加上/construction'


run(host='localhost', port=8080, reloader=True, debug=True)