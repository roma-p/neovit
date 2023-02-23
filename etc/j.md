# 22/02/23 -------------------------------------------------------------------- 

x create the basic hierarchy.
x find way to colorize tree leafs.
- pass standardize data to tree leafs (there is a way to pass non 
    formatted data to leaf, create a dto to pass)
- Then move on to tree view I guess ...


-> fastest struct key index is new python is dataclass according tests on stackoverflow
-> data_class_slots?? what is it?

# 10/02/23 -------------------------------------------------------------------

 ROADMAP: nothing clear at all, so just push dirty codes who do stuff i guess.
	- hierarchy of disto repo in left side.
	- hierrachy of local repo above
			- color code if local changes / not in repo / up to date etc...
	- displaying vit commit tree for on package.


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
