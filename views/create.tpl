<html>
    <head>
		<title>构建结果</title>
    </head>
    <body>
    <table border=1">
            <tr>
                <th>属性</th>
                <th>取值</th>
            </tr>

            <tr>
            <td><b>图数据库名称</b></td>
            <td>{{database}}</td>
            </tr>

            <tr>
            <td><b>数据源名称</b></td>
            <td>{{source}}</td>
            </tr>

            <tr>
            <td><b>文档选择</b></td>
            <td>{{document}}</td>
            </tr>

            <tr>
            <td><b>节点类型</b></td>
            <td>{{node}}</td>
            </tr>

            <tr>
            <td><b>关系类型</b></td>
            <td>{{relation}}</td>
            </tr>

            <tr>
            <td><b>节点总数目</b></td>
            <td>{{node_number}}</td>
            </tr>

            <tr>
            <td><b>边总数目</b></td>
            <td>{{edge_number}}</td>
            </tr>

            <tr>
            <td><b>net type(供展示可删除)</b></td>
            <td>{{nettype}}</td>
            </tr>

            <tr>
            <td><b>weight type(供展示可删除)</b></td>
            <td>{{weighttype}}</td>
            </tr>
        </table>
    <br/>
    <br/>
    <form action="/analysis" method="get">
            <input type="hidden" name="graphname" value={{database}} />
            <input type="hidden" name="graphtype" value="self">
            <input type="hidden" name="nettype" value={{nettype}} />
            <input type="hidden" name="weighttype" value={{weighttype}}>
            <input type="hidden" name="node" value={{node}} />
            <input type="hidden" name="relation" value={{relation}}>
            <input value="开始网络分析" type="submit" />
    </form>
    <a href="http://localhost:8080/construction">不满意，返回重新构建</a>
    </body>
</html>

