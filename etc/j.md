# 30/12/22 -------------------------------------------------------------------

rework of UI : 

1: tree, 2 : list of branches / tag (and dependencies!): : 3: graph (overall graph or graph by
branch /tag)

# Roadmap for TUI POC:
- fetch module in vit: 
	- able to fetch all data from this module: hierarchy, asset data and working copy
	- tests U ok on this (and later maybe, add a fetch feature to simplify reste of code)
- write "service layer func" (or controller, don't really know...)
	-> test model is up to date with a repo path set to something...
- update tree somethow. 
- do the same with async task.

==> implying fetching is done with command line. 
(but need to connect to server with interface will come soon...)

# 30/12/22 -------------------------------------------------------------------

-> sub widget of app and not change app directly? 
