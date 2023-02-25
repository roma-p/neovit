import os
from dataclasses import dataclass
from vit.vit_lib import fetch, infos, asset, package
from graph import Graph


class AssetCheckoutStatus:
    untracked = "untracked"
    read_only = "readonly"
    editable = "editable"


@dataclass
class AssetFileInfo:
    file_name: str
    full_path: str

    asset_status: AssetCheckoutStatus
    changes: bool
    # missing: branch / tag etc ...


class VitRepoModel(object):

    def __init__(self, repo_local_path):
        self.repo_local_path = os.path.normpath(repo_local_path)
        self.repo_name = os.path.basename(repo_local_path)
        # -- vit repo raw data (from vit_lib)
        self.vit_track_data = None
        self.local_file_structure = None
        self.origin_repo_structure = None

        # -- custom data.
        self.vit_local_repo_tree = None
        self.vit_asset_commit_tree = None
        self.editable_asset_list = None
        self.vit_asset_graph_data = None

    def build(self):

        # 1 -- fetching data from repo using vit lib
        self.vit_track_data = infos.get_track_info_neovit(self.repo_local_path)
        self.local_file_structure = [item for item in os.walk(self.repo_local_path)]
        self.origin_repo_structure = fetch.get_repo_hierarchy(self.repo_local_path)

        # 2 -- reorganizing data for nvit.
        self.vit_local_repo_tree = self.gen_local_repo_tree()
        self.editable_asset_list = self.gen_editable_asset_list()
        self.vit_asset_commit_tree = self.gen_asset_commit_tree()

        # 3 -- creating data for graphs
        self.vit_asset_graph_data = self.gen_graph_data()

    def gen_local_repo_tree(self):
        """
        format of dict:
            {
                <dir name> = {
                    directories = {
                        ...
                    }
                    assets = (
                        (
                            <asset_file_name>,
                            <asset_full_path>
                            <status: editable / readonly / untracked>,
                            <changes: True/False>
                        )
                    )
                }
            }
        """

        ret = {
        }

        def get_dict_entry_to_update(path):
            if not path:
                return ret
            entry_to_update = ret
            path = os.path.normpath(path)
            for _dir in path.split(os.sep):
                entry_to_update = entry_to_update[_dir]["directories"]
            return entry_to_update

        for (dirpath, dirnames, filenames) in self.local_file_structure:
            # ignoring hidden files.
            if dirpath == self.repo_local_path:
                continue

            dirpath = dirpath.split(self.repo_local_path+"/")[1]
            if dirpath.startswith("."):
                continue

            dir_parent_dir = os.path.dirname(dirpath)
            dir_name = os.path.basename(dirpath)

            assets = list()

            for filename in filenames:

                if filename.startswith("."):
                    continue

                file_full_path = os.path.join(dirpath, filename)

                file_track_data = self.vit_track_data.get(file_full_path, None)
                if file_track_data is not None:
                    if file_track_data["editable"]:
                        file_status = AssetCheckoutStatus.editable
                    else:
                        file_status = AssetCheckoutStatus.read_only
                    assets.append(
                        AssetFileInfo(
                            file_name=filename,
                            full_path=file_full_path,
                            asset_status=file_status,
                            changes=file_track_data["changes"]
                        )
                    )
                else:
                    assets.append(
                        AssetFileInfo(
                            file_name=filename,
                            full_path=file_full_path,
                            asset_status=AssetCheckoutStatus.untracked,
                            changes=False
                        )
                    )

            entry_to_update = get_dict_entry_to_update(dir_parent_dir)
            entry_to_update[dir_name] = {
                "directories": {
                },
                "assets": assets
            }

        return ret

    def gen_editable_asset_list(self):
        ret = []
        for file_path, file_data in self.vit_track_data.items():
            if not file_data["editable"]:
                continue
            ret.append(
                AssetFileInfo(
                    file_name=file_path,
                    full_path=os.path.join(
                        file_data["package_path"],
                        file_data["asset_name"]
                    ),
                    asset_status=AssetCheckoutStatus.editable,
                    changes=file_data["changes"]
                )
            )
        return ret

    def gen_asset_commit_tree(self):
        ret = {}
        package_list = package.list_packages(self.repo_local_path)
        for p in package_list:
            asset_list = asset.list_assets(self.repo_local_path, p)
            for a in asset_list:
                asset_full_path = os.path.join(p, a)
                tree_data = asset.get_asset_tree_info(
                    self.repo_local_path,
                    p, a
                )
                tree_data["asset"] = a
                tree_data["package"] = p
                ret[asset_full_path] = tree_data
        return ret

    def gen_graph_data(self):
        ret = {}
        for file_path, tree_data in self.vit_asset_commit_tree.items():
            graph_generator = Graph(tree_data)
            ret[file_path] = graph_generator.gen_graph()
        return ret


if __name__ == "__main__":
    # print(VitRepoModel().get_local_repo_tree())
    vitRepoModel = VitRepoModel(os.getcwd())
    vitRepoModel.build()
    # pprint.pprint(vitRepoModel.vit_asset_commit_tree)
    # pprint.pprint(vitRepoModel.editable_asset_list)
