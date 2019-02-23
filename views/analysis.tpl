<html>
    <head>
		<title>网络分析</title>
		<script language="javascript">
		//创建一个show/hidediv的方法，直接跟ID属性
		function showdiv(id){
			var sbtitle=document.getElementById(id);
			if(sbtitle){
			   sbtitle.style.display='block';
			}
		}
		function hidediv(id){
			var sbtitle=document.getElementById(id);
			if(sbtitle){
			   sbtitle.style.display='none';
			}
		}
		</script>
    </head>
    <body>
        %if graphtype == "self":
        <p><h1>选择网络：原始网络</h1></p>
        %elif graphtype == "component":
        <p><h1>选择网络：最大主成分</h1></p>
        %elif graphtype == "ego":
        <p><h1>选择网络：个体网</h1></p>
        %elif graphtype == "community":
        <p><h1>选择网络：社区</h1></p>
		%end
		%if graphtype == "community":
		%for i, c in enumerate(g):
		<p><h2>基本分析-社区{{i+1}}</h2></p>
        <table border=1>
            <tr>
                <td><b>节点数</b></td>
                <td>{{c.scale}}</td>
            </tr>
            <tr>
                <td><b>边数</b></td>
                <td>{{c.size}}</td>
            </tr>
            <tr>
                <td><b>平均点度数</b></td>
                <td>{{round(c.aver_degree, 4)}}</td>
            </tr>
            <tr>
                <td><b>网络密度</b></td>
                <td>{{round(c.density, 4)}}</td>
            </tr>
        </table>
        <hr />
        <p><h2>节点列表</h2></p>
        <table border=1 id="nodelist">
            <tr>
                <th>节点</th>
                <th>中心度</th>
            </tr>
            %import networkx as nx
            %names = nx.get_node_attributes(c.network, 'name')
            %for item in c.find_nodes_by_centrality(c_type='degree', n=10):
            <tr>
            <td><b>{{names[item[0]]}}</b></td>
            <td>{{round(item[1], 4)}}</td>
            </tr>
            %end
        </table>
		<br />
		<button type="button">首页</button>
		<button type="button">上一页</button>
		<button type="button">下一页</button>
		<button type="button">尾页</button>
		<hr />
		%end
		%else:
        <p><h2>基本分析</h2></p>
        <table border=1>
            <tr>
                <td><b>节点数</b></td>
                <td>{{g.scale}}</td>
            </tr>
            <tr>
                <td><b>边数</b></td>
                <td>{{g.size}}</td>
            </tr>
            <tr>
                <td><b>平均点度数</b></td>
                <td>{{round(g.aver_degree, 4)}}</td>
            </tr>
            <tr>
                <td><b>网络密度</b></td>
                <td>{{round(g.density, 4)}}</td>
            </tr>
        </table>
        <hr />
        <p><h2>节点列表</h2></p>
        <table border=1 id="nodelist">
            <tr>
                <th>节点</th>
                <th>中心度</th>
            </tr>
            %import networkx as nx
            %names = nx.get_node_attributes(g.network, 'name')
            %for item in g.find_nodes_by_centrality(c_type='degree', n=10):
            <tr>
            <td><b>{{names[item[0]]}}</b></td>
            <td>{{round(item[1], 4)}}</td>
            </tr>
            %end
        </table>
		<br />
		<button type="button">首页</button>
		<button type="button">上一页</button>
		<button type="button">下一页</button>
		<button type="button">尾页</button>
		<hr />
		%end
		%if graphtype != "self":
		<form action="/analysis" method="get">
            <input type="hidden" name="graphname" value={{graphname}}>
			<input type="hidden" name="graphtype" value="self">
            <input value="返回主网络" type="submit" />
        </form>
		%else:
        <form action="/analysis" method="get">
            <label>可抽取网络特定部分：</label>
            <input type="hidden" name="graphname" value={{graphname}}>
            <input name="graphtype" type="radio" value="self" onclick='hidediv("ego_core")';>原始网络</input>
			<input name="graphtype" type="radio" value="component" onclick='hidediv("ego_core")';>最大主成分</input>
			<input name="graphtype" type="radio" value="ego" onclick='showdiv("ego_core")';>个体网</input>
			<input name="graphtype" type="radio" value="community" onclick='hidediv("ego_core")';>社区</input>
			<br />
			<div id="ego_core" style="display:none">
				请选择个体网的中心节点：
				<select name="ego_core">
					%for item in g.find_nodes_by_centrality(c_type='degree', n=10):
					<option value='{{item[0]}}'>{{names[item[0]]}}</option>
					%end
				</select>
				<br />
				请选择个体网的步长：
				<select name="ego_radius">
					<option value='1' selected="selected">1</option>
					<option value='2'>2</option>
					<option value='3'>3</option>
				</select>
			</div>
            <input value="抽取" type="submit" />
        </form>
		%end
     <br />
     <br />
     <a href="http://localhost:8080/construction">返回构建新的网络</a>
    </body>
</html>