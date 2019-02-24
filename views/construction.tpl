<html>
    <head>
		<title>网络构建</title>
    </head>
    <body>

    <form action="/construction" method="get">
        您想要创建的网络类型？<br /><br />
        <label><input name="graphtype" type="radio" value="text" />词语网络</label>
        <br /><label><input name="graphtype" type="radio" value="author" />作者网络</label>
        <br /><label><input name="graphtype" type="radio" value="paper" />引文网络</label>
        <br /><label><input name="graphtype" type="radio" value="other" />paper_author网络 或者 paper_word网络</label>
        <br /><br />
        <input value="确定" type="submit" />
    </form>

    %if graphtype == "text":
    <p><h3>构建词语网络</h3></p>
    <form action="/text" method="post">
        请输入图数据库的名称: <input name="database" type="text" /><br/>
        请选择数据源:
        <label><input name="source" type="radio" value="ScienceDirectDataSource" />ScienceDirectDataSource(共200篇文献)</label>
        <label><input name="source" type="radio" value="Other" />Other</label><br/>
        请输入建图文献范围(示例写法：1-20): <input name="document" type="text" /><br/>
        请选择节点类型:
        <label><input name="node" type="radio" value="noun" />名词</label>
        <label><input name="node" type="radio" value="adj" />形容词</label>
        <label><input name="node" type="radio" value="verb" />动词</label>
        <label><input name="node" type="radio" value="noun_phrase" />名词短语</label>
        <label><input name="node" type="radio" value="keyword" />关键词</label>
        <label><input name="node" type="radio" value="ner" />命名实体</label>
        <br/>
        请输入关系类型：
        <label><input name="relation" type="radio" value="co" />共现关系</label>
        <label><input name="relation" type="radio" value="wordnet" />WordNet相似度(速度慢)</label>
        <br/><br/>
        <input value="开始构建" type="submit" />
    </form>

    %elif graphtype == "author":
    <form action="/author" method="post">
        请输入图数据库的名称: <input name="database" type="text" /><br/>
        请选择数据源:
        <label><input name="source" type="radio" value="ScienceDirectDataSource" />ScienceDirectDataSource(共200篇文献)</label>
        <label><input name="source" type="radio" value="Other" />Other</label><br/>
        请输入建图文献范围(示例写法：1-20): <input name="document" type="text" /><br/>
        请输入关系类型：
        <label><input name="relation" type="radio" value="all" />cite</label>
        <br/><br/>
        <input value="开始构建" type="submit" />
    </form>

    %elif graphtype == "paper":
    <form action="/paper" method="post">
        请输入图数据库的名称: <input name="database" type="text" /><br/>
        请选择数据源:
        <label><input name="source" type="radio" value="ScienceDirectDataSource" />ScienceDirectDataSource(共200篇文献)</label>
        <label><input name="source" type="radio" value="Other" />Other</label><br/>
        请输入建图文献范围(示例写法：1-20): <input name="document" type="text" /><br/>
        请输入关系类型：
        <label><input name="relation" type="radio" value="cite" />cite关系</label>
        <br/><br/>
        <input value="开始构建" type="submit" />
    </form>


    %elif graphtype == "other":
    <form action="/other" method="post">
        请输入图数据库的名称: <input name="database" type="text" /><br/>
        请选择数据源:
        <label><input name="source" type="radio" value="ScienceDirectDataSource" />ScienceDirectDataSource(共200篇文献)</label>
        <label><input name="source" type="radio" value="Other" />Other</label><br/>
        请输入建图文献范围(示例写法：1-20): <input name="document" type="text" /><br/>
        请输入关系类型：
        <label><input name="relation" type="radio" value="paper_author" />paper_author关系</label>
        <label><input name="relation" type="radio" value="paper_word" />paper_word关系</label>
        <br/><br/>
        <input value="开始构建" type="submit" />
    </form>
    %end

    </body>
</html>

