from bottle import route, view, run, request, template
import network_analysis.network as network


@route('/load')
def analysis():
    return template('loadgraph')


@route('/analysis', method='get')
@view('analysis')
def do_analysis():
    gname = request.query.graphname
    gtype = request.query.graphtype
    g = network.Net(gname, net_type='author citation network', weight_type='cite_count')
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


run(host='127.0.0.1', port='8080', debug=True)
