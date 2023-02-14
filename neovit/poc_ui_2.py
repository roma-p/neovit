import os
import logging
from vit.vit_lib import fetch, infos
from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Tree, Button

from vit_repo_model import VitRepoModel

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class NeoVit(App):
    CSS_PATH = "neovit.css"

    BINDINGS = [
        ("r", "refresh", "refresh view from current metadata")
    ]

    def compose(self) -> ComposeResult:

        self.vit_repo_model = VitRepoModel(os.getcwd())
        self.vit_repo_model.build()

        yield Header("neovit")
        yield TopBandWidget("band", classes="box")
        yield ControlView("control", classes="box", id="two")
        yield RepoView("repo", classes="box", id="repoView")

    def action_refresh(self) -> None:
        tree = self.query_one(DistantRepoView)
        # tree.root.add("jinx", expand=True)


class TopBandWidget(Static):
    pass


class RepoView(Static):
    def compose(self):
        repo_config = infos.get_vit_config(os.getcwd())
        repo_link = repo_config["origin_link"]["path"]
        repo_name = os.path.basename(repo_link)
        yield LeftContainer(repo_name,  classes="stuff")
        yield AssetView("graph", classes="box")


class ControlView(Static):
    pass


class GraphRow(Button):
    def compose(self):
        yield GraphRowGraph()
        yield GraphRowMessage()


class GraphRowGraph(Static):

    def render(self):
        return " | \n | "


class GraphRowMessage(Static):
    def render(self):
        return "blou blou"


class LeftContainer(Static):

    def compose(self):
        yield DistantRepoView("distant", classes="box")
        yield DistantRepoView("local")


class DistantRepoView(Tree):

    def compose(self):
        # check if vit repo. TODO: better centralize way to do it...
        if not os.path.exists(".vit"):
            return set()
        data = fetch.get_repo_hierarchy(os.getcwd())

        def _add_package(parent_node, package_name, children_data):
            package_node = parent_node.add(package_name, expand="True")
            for sub_package_name, sub_package_data in children_data["packages"]:
                _add_package(package_node, sub_package_name, sub_package_data)
            for sub_asset_name in children_data["assets"]:
                _add_asset(package_node, sub_asset_name)

        def _add_asset(parent_node, asset_name):
            parent_node.add_leaf(asset_name)
        self.root.expand()
        for package_name, package_data in data.items():
            _add_package(self.root, package_name, package_data)
        print(get_local_repo_tree())
        return set()

    def NodeSelected(self, *args, **kargs):
        print("prout")


def get_local_repo_tree():
    """
    format of dict:
        {
            <dir name> = {
                directories = {
                    ...
                }
                untracked_files = (),
                assets = (
                    (<asset_file_name>, <status>)
                )
            }
        }
    """

    vit_local_data = infos.get_info_from_all_ref_files(os.getcwd())
    file_structure = os.walk(os.getcwd())
    ret = {
    }

    def get_dict_entry_to_update(path):
        entry_to_update = ret
        path = os.path.normpath(path)
        log.info(path)
        for _dir in path.split(os.sep):
            log.info(_dir)
            # entry_toupdate["directories"][_dir]
        # return entry_to_update
        return {}

    for (dirpath, dirnames, filenames) in file_structure:
        # ignoring hidden files.
        if "./" in dirpath:
            continue

        dir_parent_dir = os.path.dirname(dirpath)
        dir_name = os.path.basename(dirpath)

        untracked_files = list()
        assets = list()

        for filename in filenames:
            file_full_path = os.path.join(dirpath, filename)
            if file_full_path not in vit_local_data:
                untracked_files.append(filename)
            else:
                assets.append((filename, vit_local_data[file_full_path["changes"]]))

        entry_to_update = get_dict_entry_to_update(dir_parent_dir)
        entry_to_update[dir_name] = {
            "directories": {
            },
            "untracked_files": untracked_files,
            "assets": assets
        }
    return ret


class AssetView(Static):
    def compose(self):
        yield GraphRow()
        yield GraphRow()
        yield GraphRow()
        yield GraphRow()


if __name__ == "__main__":
    app = NeoVit()
    app.run()
