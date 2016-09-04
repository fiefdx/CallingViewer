CallingViewer
=============
A golang project code viewer developed by python, it has project tree view and project method calling/called tree view, and you can open the source code from the two views, so, it can help you to understand a golang project quickly.

Install CallingViewer
---------------------
1. need to install golang callgraph
2. need to install python-setuptools, python-tornado, python-whoosh, python-jieba, python-chardet, python-toro

Run CallingViewer
-----------------
1. config configuration.yml file, specify host, port or log_level
2. python CallingViewer.py # start CallingViewer service
3. open browser with http://localhost:9009
4. add a golang project, click the Add button at bottom-left, fill the form then click Add
5. after add a golang project, you can see the project's tree view left
6. type method's name into search input, click Search button, you can get the calling view