<html>
    <head>
    <title>图数据读取中</title>
    </head>
    <body>
        <p><h2>请输入图名称（带文件后缀）</h2></p>
        <form action="/analysis" method="get">
            Graph Name: <input name="graphname" type="text" />
            <input type="hidden" name="graphtype" value="self">
            <input value="分析" type="submit" />
        </form>
    </body>
</html>