import os
from dataclasses import dataclass
from vit_repo_model import VitRepoModel, AssetCheckoutStatus
from graph import GraphDataCommit, GraphDataTags, GraphDataBranch

# textual imports
from textual.containers import Container, Horizontal, Vertical
from textual.app import ComposeResult, App
from textual.widgets import Static, Header, Tree, Footer, _tree, Button

from rich.text import Text, TextType


class TreeColor:
    editable_change = "red3"
    editable_no_change = "indian_red"
    readonly_change = "green3"
    readonly_no_change = "see_green3"
    untracked_file = "grey46"


def get_asset_color(asset_data):
    if asset_data.asset_status == AssetCheckoutStatus.untracked:
        return TreeColor.untracked_file
    if asset_data.asset_status == AssetCheckoutStatus.editable:
        if asset_data.changes:
            return TreeColor.editable_change
        else:
            return TreeColor.editable_no_change
    else:
        if asset_data.changes:
            return TreeColor.readonly_change
        else:
            return TreeColor.readonly_no_change


class RepoModelWrapper(object):
    _repo_model = None
    current_asset = None

    @classmethod
    def init_repo_model(cls):
        if cls._repo_model is None:
            cls._repo_model = VitRepoModel(os.getcwd())
            cls._repo_model.build()

    @classmethod
    def get_repo_model(cls):
        return cls._repo_model

    @classmethod
    def get_graph_data(cls):
        repo_model = cls.get_repo_model()
        tmp = repo_model.vit_asset_graph_data.get(cls.current_asset, None)
        return tmp.graph_commit_item_list


class NeoVit(App):

    CSS_PATH = "main.css"

    def on_mount(self):
        RepoModelWrapper.init_repo_model()

    def compose(self) -> ComposeResult:
        RepoModelWrapper.init_repo_model()
        yield Header("neovit")
        yield Container(
            RepoView(
                RepoModelWrapper.get_repo_model().repo_name,
                id="left-pane",
            ),
            AssetView(
                id="top-right"
            ),
            id="app-grid",
        )
        yield Footer()

    def on_tree_node_selected(self, event):
        event.stop()
        data = event.node.data
        if data is None:
            return
        asset_view = self.query_one("#top-right", AssetView)
        asset_view.set_asset_tree_view(data.full_path)


def _add(
        self,
        label: TextType,
        data=None,
        *,
        expand: bool = False,
        allow_expand: bool = True):

    color = None
    if data is not None:
        color = get_asset_color(data)

    text_label = self._tree.process_label(label, color)
    node = self._tree._add_node(self, text_label, data)
    node._expanded = expand
    node._allow_expand = allow_expand
    self._updates += 1
    self._children.append(node)
    self._tree._invalidate()
    return node
_tree.TreeNode.add = _add


class RepoView(Tree):

    def process_label(self, label: TextType, color: str = None):
        if isinstance(label, str):
            text_label = Text.from_markup(label)
        else:
            text_label = label
        first_line = text_label.split()[0]
        if color:
            first_line.stylize(color)
        return first_line

    def compose(self):
        repo_model = RepoModelWrapper.get_repo_model()
        self.root.expand()
        self._update_local_editable(repo_model)
        self._update_local_structure(repo_model)
        self._update_origin_structure(repo_model)
        return set()

    def _update_local_editable(self, repo_model):
        editable = self.root.add("editable")
        editable.expand()
        for asset_data in repo_model.editable_asset_list:
            editable.add_leaf(asset_data.file_name, data=asset_data)

    def _update_local_structure(self, repo_model):
        local_repo = self.root.add("local repo")
        repo_structure_data = repo_model.vit_local_repo_tree

        def _add_package(parent_node, package_name, children_data):
            package_node = parent_node.add(package_name, expand="True")
            for sub_package_name, sub_package_data in children_data["directories"].items():
                _add_package(package_node, sub_package_name, sub_package_data)
            for sub_asset in children_data["assets"]:
                _add_asset(package_node, sub_asset)

        def _add_asset(parent_node, asset_data):
            parent_node.add_leaf(asset_data.file_name, data=asset_data)

        local_repo.expand()
        for package_name, package_data in repo_structure_data.items():
            _add_package(local_repo, package_name, package_data)

    def _update_origin_structure(self, repo_model):
        origin_repo = self.root.add("origin repo")
        repo_structure_data = repo_model.origin_repo_structure

        def _add_package(parent_node, package_name, children_data):
            package_node = parent_node.add(package_name, expand="True")
            for sub_package_name, sub_package_data in children_data["packages"]:
                _add_package(package_node, sub_package_name, sub_package_data)
            for sub_asset_name in children_data["assets"]:
                _add_asset(package_node, sub_asset_name)

        def _add_asset(parent_node, asset_name):
            parent_node.add_leaf(asset_name)
        origin_repo.expand()
        for package_name, package_data in repo_structure_data.items():
            _add_package(origin_repo, package_name, package_data)


@dataclass
class AssetTreeDataCommit():
    tree_data: str
    commit_mess: str
    user: str
    date: float
    commit_id: str


class AssetTreeView(Vertical):
    def compose(self):
        tree_data = RepoModelWrapper.get_graph_data()
        if not tree_data:
            return ()
        for graph_item_data in tree_data:
            yield AssetTreeItem(tree_data=graph_item_data)


class GraphRowGraph(Static):
    pass


class GraphRowMessage_Commit(Vertical):

    def __init__(self, *args, tree_data=None, **kargs):
        super().__init__(*args, **kargs)
        self.tree_data = tree_data

    def compose(self):
        yield Static(self.tree_data.commit_mess)
        yield Static("{} : {}".format(self.tree_data.user, self.tree_data.date))
        yield Static(self.tree_data.commit_id)


class GraphRowMessage_Branch(Vertical):

    def __init__(self, *args, tree_data=None, **kargs):
        super().__init__(*args, **kargs)
        self.tree_data = tree_data

    def compose(self):
        yield Static(self.tree_data.branch)


class GraphRowMessage_Tag(Vertical):

    def __init__(self, *args, tree_data=None, **kargs):
        super().__init__(*args, **kargs)
        self.tree_data = tree_data

    def compose(self):

        yield Static(self.get_tag_line())
        yield Static(self.tree_data.commit_mess)
        yield Static("{} : {}".format(self.tree_data.user, self.tree_data.date))
        yield Static(self.tree_data.commit_id)

    def get_tag_line(self):
        tag_line = "TAG: "
        for tag in self.tree_data.tags:
            tag_line += tag + ", "
        tag_line = tag_line[:-2]
        return tag_line

class GraphRowMessage_Branch(Vertical):

    def __init__(self, *args, tree_data=None, **kargs):
        super().__init__(*args, **kargs)
        self.tree_data = tree_data

    def compose(self):
        yield Static(self.tree_data.branch)


class AssetTreeItem(Horizontal):

    def __init__(self, *args, tree_data=None, **kargs):
        super().__init__(*args, **kargs)
        self.tree_data = tree_data

    # A GRID
    # BUTTON is TWO full F
    # but not the other...

    def compose(self):
        graph_str = ""
        for line in self.tree_data.lines:
            graph_str += line + "\n"
        # yield Button("", id="transparent_button")
        yield GraphRowGraph(graph_str)
        if isinstance(self.tree_data, GraphDataCommit):
            yield GraphRowMessage_Commit(tree_data=self.tree_data)
        elif isinstance(self.tree_data, GraphDataBranch):
            yield GraphRowMessage_Branch(tree_data=self.tree_data)
        else:
            yield GraphDataTags(tree_data=self.tree_data)


class AssetView(Vertical):

    def compose(self):
        return ()

    def set_asset_tree_view(self, file_path):
        if RepoModelWrapper.current_asset == file_path:
            return
        RepoModelWrapper.current_asset = file_path
        try:
            assetTreeView = self.query_one(AssetTreeView)
        except Exception:  # NoMatches
            pass
        else:
            assetTreeView.remove()
        item = AssetTreeView(id="asset-tree-view")
        self.mount(item)


if __name__ == "__main__":
    app = NeoVit()
    app.run()
