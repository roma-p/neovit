import os
import unittest
from vit.vit_lib.misc import tree_func
from neovit.utils import cycle_branch_color
from neovit.graph import Graph

from vit.vit_lib import (
    checkout, tag,
    commit, branch
)

from tests import vit_test_repo as repo
from vit.connection.vit_connection import ssh_connect_auto
from rich import print as rprint


class TestGraph(unittest.TestCase):

    print_graph = False

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def _get_tree_data(self, local_path, package_path, asset_name):
        tree_asset, tree_asset_path = tree_func.get_local_tree_asset(
            local_path,
            package_path,
            asset_name
        )
        with tree_asset:
            tree_data = tree_asset.data
        return tree_data

    def test_graph_single_commit(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                repo.test_local_path_1, vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", True
            )
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file), "1")
            commit.commit_file(
                repo.test_local_path_1, vit_connection,
                checkout_file, "1", True, True
            )
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file), "2")
            commit.commit_file(
                repo.test_local_path_1, vit_connection, checkout_file,
                "2", True, True
            )
            tree_data = self._get_tree_data(repo.test_local_path_1, repo.package_ok, repo.asset_ok)
            graph_generator = Graph(tree_data)
            graph = graph_generator.gen_graph()
            # print(graph)
            # print(graph.graph_commit_item_list)
            # print("")
            for item in graph.graph_commit_item_list:
                rprint(item.lines)
                # print(type(item.lines))

    def test_cycle_branch_color(self):
        color = cycle_branch_color()
        color = cycle_branch_color()


    # def test_graph_four_branches_from_same_commit(self):
    #     with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
    #         checkout_file = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "base", True
    #         )
    #         self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file), "1")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "1", True, True
    #         )
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", branch_parent="base"
    #         )
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_2", branch_parent="base"
    #         )
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_3", branch_parent="base"
    #         )
    #         checkout_file_1 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", True
    #         ) 
    #         checkout_file_2 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_2", True
    #         ) 
    #         checkout_file_3 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_3", True
    #         )
    #
    #     self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file), "2")
    #     self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file_1), "3")
    #     self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file_2), "4")
    #     self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file_3), "5")
    #
    #     commit.commit_file(repo.test_local_path_1, vit_connection, checkout_file, "2", True, True)
    #     commit.commit_file(repo.test_local_path_1, vit_connection, checkout_file_1, "3", True, True)
    #     commit.commit_file(repo.test_local_path_1, vit_connection, checkout_file_2, "4", True, True)
    #     commit.commit_file(repo.test_local_path_1, vit_connection, checkout_file_3, "5", True, True)
    #
    #     a = graph.main(repo.test_local_path_1, repo.package_ok, repo.asset_ok)
    #     if self.print_graph:
    #         for l in a: print(l)
    #
    # def test_graph_two_branches(self):
    #     with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
    #         # one commit on trunk / on commit on each branch.
    #         checkout_file = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok, repo.asset_ok,
    #             "base", True
    #         )
    #         self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file), "1")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection, checkout_file, "1", True, True
    #         )
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", branch_parent="base"
    #         )
    #         checkout_file_1 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", True
    #         )
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file_1), "2")
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file), "3")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file_1, "2", True, True
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "3", True, True
    #         )
    #         a = graph.main(repo.test_local_path_1, repo.package_ok, repo.asset_ok)
    #         if self.print_graph:
    #             for l in a: print(l)
    #
    # def test_graph_two_branches_no_commit_after_branching_one_of_them(self):
    #     with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
    #         checkout_file = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok, "base", True
    #         )
    #         self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file), "1")
    #         commit.commit_file(
    #             repo.test_local_path_1,
    #             vit_connection,
    #             checkout_file,
    #             "1", True, True
    #         )
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", branch_parent="base"
    #         )
    #         checkout_file_1 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", True
    #         )
    #         self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file_1), "2")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file_1, "2", True, True
    #         )
    #         a = graph.main(repo.test_local_path_1, repo.package_ok, repo.asset_ok)
    #         if self.print_graph:
    #             for l in a: print(l)
    #
    # def test_graph_no_commit_after_branch(self):
    #     with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
    #         checkout_file = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "base", True
    #         )
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file), "1")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "1", True, True
    #         )
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", branch_parent="base"
    #         )
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_2", branch_parent="base"
    #         )
    #         checkout_file_1 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", True
    #         )
    #         self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file_1), "2")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file_1, "2", True, True
    #         )
    #         a = graph.main(repo.test_local_path_1, repo.package_ok, repo.asset_ok)
    #         if self.print_graph:
    #             for l in a: print(l)
    #
    # def test_graph_heavy(self):
    #
    #     with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
    #
    #         # checkout and commit "1" on base
    #
    #         checkout_file = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok, "base", True
    #         )
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file), "1"
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "1", True, True
    #         )
    #
    #         # branching "branch_1" from base and commit 2 on branch 1
    #
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", branch_parent="base", create_tag=True
    #         )
    #         checkout_file_1 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", True
    #         )
    #         self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file_1), "2")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file_1, "2", True, True
    #         )
    #
    #         # commit 3 on branch 1
    #
    #         self._append_line_to_file(os.path.join(repo.test_local_path_1, checkout_file), "3")
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "3", True, True
    #         )
    #         tag.create_tag_light_from_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "branch_1", "my_first_tag"
    #         )
    #
    #         # commit 4 on branch 1
    #
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file_1), "4"
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file_1, "4", True, True
    #         )
    #         tag.create_tag_annotated_from_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "branch_1", "tag_annotated_test", "blou blou blou"
    #         )
    #         tag.create_tag_light_from_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "branch_1", "oups_i_tagged_again"
    #         )
    #
    #         # branch_2 from base.
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "branch_2", branch_parent="base", create_tag=True
    #         )
    #
    #         # branch_2 from base.
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "branch_2_1", branch_parent="branch_2", create_tag=True
    #         )
    #
    #         # branch_2 from base.
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "branch_2_2", branch_parent="branch_2", create_tag=True
    #         )
    #
    #         # commit 5 on branch_1
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file), "5"
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "5", True, True
    #         )
    #
    #         # commit 6 on branch_1
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file_1), "6"
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file_1, "6", True, True
    #         )
    #
    #         # branch_3 from base and checkout.
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_3", branch_parent="base", create_tag=True
    #         )
    #         checkout_file_2 = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection,
    #             repo.package_ok, repo.asset_ok,
    #             "branch_2", True
    #         )
    #
    #         # commit 7 on branch_3
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file_2), "7"
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file_2, "7", True, True
    #         )
    #
    #         # commit 8 on branch_1
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file), "8"
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "8", True, True
    #         )
    #         a = graph.main(repo.test_local_path_1, repo.package_ok, repo.asset_ok)
    #         if self.print_graph:
    #             for l in a: print(l)
    #
    # def test_graph_two_branches_at_first_commit(self):
    #     with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
    #         # one commit on trunk / on commit on each branch.
    #         branch.create_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", branch_parent="base", create_tag=True
    #         )
    #         checkout_file = checkout.checkout_asset_by_branch(
    #             repo.test_local_path_1, vit_connection, repo.package_ok,
    #             repo.asset_ok, "branch_1", True
    #         )
    #         self._append_line_to_file(os.path.join(
    #             repo.test_local_path_1, checkout_file), "voila"
    #         )
    #         commit.commit_file(
    #             repo.test_local_path_1, vit_connection,
    #             checkout_file, "voila", True, True
    #         )
    #         a = graph.main(repo.test_local_path_1, repo.package_ok, repo.asset_ok)
    #
    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
