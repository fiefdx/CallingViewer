CallingViewer
=============
A golang project code viewer developed by python, it has project tree view and project method calling/called tree view, and you can open the source code from the two views, so, it can help you to understand a golang project quickly.

Install CallingViewer
---------------------
1. need to install golang callgraph, guru
2. need to install python-setuptools, python-tornado, python-whoosh, python-jieba, python-chardet, python-toro
   ```bash
   # install callgraph & guru
   sudo apt-get install golang-golang-x-tools

   # install packages use pip
   cd ./CallingViewer/requires
   sudo pip install -r requirements.txt

   # or install packages use apt-get at Ubuntu
   sudo apt-get install python-setuptools python-tornado python-whoosh python-chardet python-toro
   sudo easy_install toro
   ```

Run CallingViewer
-----------------
1. config configuration.yml file, specify host, port or log_level
   ```yaml
   app_debug: true

   # LOG_LEVEL
   # a value of (NOSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)
   # default NOSET
   log_level: DEBUG

   server_host: 127.0.0.1
   server_port: 9009

   db_type: bsddb

   # DATA_PATH
   # a path for all data
   # data_path: /home/breeze/Develop/CallingViewer/DATA
   ```
2. python CallingViewer.py # start CallingViewer service
3. open browser with http://localhost:9009

   _ex. the main window like below_

   ![Alt text](/doc/main_window.png?raw=true "main_window")

4. add a golang project, click the Add button at bottom-left, fill the form then click Add
 * Project Name: is the name will display at the top-left select box
 * Project Path: is the root directory path will be the root of the left tree view
 * Go Path: is the environment variable $GOPATH for the Project, eg: /home/user/work/project:/home/user/work/lib
 * Main Path: is the golang Project's main source file path, which file is what you want to analyze, eg: /home/user/work/project/main.go

   _ex. github.com/flike/idgo fill the form like below_

   ![Alt text](/doc/add_project.png?raw=true "add_project")

5. after add a golang project, you can see the project's tree view left, right click the node, you can get context menu, left click the menu you can open a new tab with the source code

   _ex. project's tree view like below_

   ![Alt text](/doc/project_tree_view_with_context_menu.png?raw=true "project_tree_view_with_context_menu")

   _ex. open source code from project's tree view like below_

   ![Alt text](/doc/open_source_code_by_project_context_menu.png?raw=true "open_source_code_by_project_context_menu")

6. type method's name into search input, click Search button, you can get the calling view, if you want the called view, you can select the "Called" option, then click Search button, right click the node, you can get context menu, left click the menu you can open a new tab with the source code where the function be calling/called

   _ex. calling view like below_

   ![Alt text](/doc/calling_tree_view_with_context_menu.png?raw=true "calling_tree_view_with_context_menu")

   _ex. open source code from calling view like below_

   ![Alt text](/doc/open_source_code_by_tree_context_menu.png?raw=true "open_source_code_by_tree_context_menu")

7. you can type keyword in the "Filter" input, so, it will just display the result contained the keyword

8. in the code editor, you can select a key word and right click, then get a context menu, you can use the context menu to 'Go To Definition' or 'Find Referrers', click the context menu ro click the referrers list item, you can open the specified source code file in a new browser tab

  _ex. get editor context menu like below_

  ![Alt text](/doc/editor_context_menu.png?raw=true "editor_context_menu")

  _ex. get referrers list like below_

  ![Alt text](/doc/editor_referrers_list.png?raw=true "editor_referrers_list")
