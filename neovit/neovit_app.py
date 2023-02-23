import os
from vit_repo_model import VitRepoModel, AssetCheckoutStatus

# textual imports
from textual.containers import Container, Horizontal, Vertical
from textual.app import ComposeResult, App
from textual.widgets import Static, Header, Tree, Footer, _tree

from rich.text import Text, TextType


class TreeColor:
    editable_change    = "red3"
    editable_no_change = "indian_red"
    readonly_change    = "green3"
    readonly_no_change = "see_green3"
    untracked_file     = "grey46"


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

    @classmethod
    def init_repo_model(cls):
        if cls._repo_model is None:
            cls._repo_model = VitRepoModel(os.getcwd())
            cls._repo_model.build()

    @classmethod
    def get_repo_model(cls):
        return cls._repo_model


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
            Horizontal(
                id="top-right"
            ),
            id="app-grid",
        )
        yield Footer()


def add(
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


_tree.TreeNode.add = add


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

if __name__ == "__main__":
    app = NeoVit()
    app.run()
