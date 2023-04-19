from dataclasses import dataclass
import utils
import graph_func


@dataclass
class GraphDataCommit():
    lines: tuple[str]
    commit_id: str
    commit_mess: str
    user: str
    date: int


@dataclass
class GraphDataTags():
    lines: tuple[str]
    tags: tuple[str]
    commit_id: str
    user: str
    date: int


@dataclass
class GraphDataBranch():
    lines: tuple[str]
    branch: str


class GraphDataHolder():

    def __init__(self):
        self.max_graph_len = 0
        self.graph_data_item_list = []

        self._line_buffer = []
        self._graph_data_item_buffer = None

    def set_buffer(self, graph_data_item):
        self._graph_data_item_buffer = graph_data_item

    def flush_buffer(self):
        if self._graph_data_item_buffer is not None:
            self._graph_data_item_buffer.lines = tuple(self._line_buffer)
            self.graph_data_item_list.append(self._graph_data_item_buffer)
        self._line_buffer = []
        self._graph_data_item_buffer = None

    def add_buffer_lines(self, *lines):
        self._line_buffer += lines


class GraphData():
    def __init__(
            self,
            graph_commit_item_list,
            graph_branch_item_list,
            graph_tag_item_list):
        self.graph_commit_item_list = graph_commit_item_list
        self.graph_branch_item_list = graph_branch_item_list
        self.graph_tag_item_list = graph_tag_item_list


class Graph(object):

    def __init__(self, tree_data):

        # parameters resolved from tree assets.
        self.tree_commits = tree_data["commits"]    # commit id to commit data for every commits
        self.tree_branches = tree_data["branches"]  # branch id to commit id for every branches.

        self.branch_tip_date = {}        # branch id to date of last commit
        self.branching_commits = {}      # commit id to number of branches branching from it.
        self.tag_index = {}              # commit to list of tags referencing this commit.

        # iterators maintained during graph generation.
        self.branch_draw_index = {}      # branch to row index where to draw branch on terminal.
        self.branch_treated = set()      # branch that already have been added to branch_draw_index
        self.branch_next_commit = {}     # branch to next commit to draw on terminal.
        self.branch_next_date = {}       # branch to date of the next commit to draw on terminal.
        self.branching_commits_rdy = {}  # branching commits to set of branches rdy to draw branching.

        self.next_branch = None          # branch id to draw on next cycle.
        self.next_branch_date = None     # date of branch to draw on next cycle.

        self.graph_holder_tags = GraphDataHolder()
        self.graph_holder_branch = GraphDataHolder()
        self.graph_holder_commits = GraphDataHolder()

    def gen_graph(self):

        # fetch data from repo and init iterators and buff.
        self._resolve_branching_commits()
        self._init_branch_next_date_and_branch_next_commit()

        # init first cycle of loop.
        self._update_next_branch()
        first_branch = self.next_branch
        self._add_branch_to_draw_index(first_branch)
        self._draw_tip_of_branch(first_branch, 1, 0)
        self._update_next_branch()

        while True:

            # -- getting branch_to_draw.
            branch_to_draw, _ = self._get_branch_to_draw()
            if branch_to_draw not in self.branch_draw_index:
                self._handle_new_branch_and_draw(branch_to_draw)

            # -- getting commit info.
            commit = self.branch_next_commit[branch_to_draw]
            commit_data = self.tree_commits[commit]
            commit_draw_index = self.branch_draw_index[branch_to_draw]
            next_commit = commit_data["parent"]

            # -- checking if commit is branching commit.
            is_branching_commit = False
            is_branching_to_draw = False
            if commit in self.branching_commits:
                is_branching_commit = True
                self._update_branching_commits_drawn(commit, branch_to_draw)
            is_branching_to_draw = self._check_is_branching_to_draw(commit)

            # -- if so, dealing with it.
            if is_branching_to_draw:
                branches_on_commit = self.branching_commits_rdy[commit]
                branches_idx = []
                for branch in branches_on_commit:
                    if branch not in self.branch_draw_index:
                        self._handle_new_branch_and_draw(branch)
                    branches_idx.append(self.branch_draw_index[branch])
                self._draw_branching(
                    len(self.branch_draw_index),
                    *branches_idx
                )
                branch_root = self._update_draw_index_after_branching(*branches_on_commit)
                self.branch_next_commit[branch_root] = next_commit
                commit_draw_index = self.branch_draw_index[branch_root]

            # -- drawning commit or tag.
            if not is_branching_commit or is_branching_to_draw:
                self._draw_commit_or_tag(commit, commit_draw_index, commit_data)

            self.branch_next_commit[branch_to_draw] = next_commit
            if self.branch_next_commit[branch_to_draw] is None:
                # -- if commit normal commit -> simple break out of loop.
                if commit not in self.branching_commits:
                    break
                # -- if commit is branching commit -> need specific treatement.

                br_idx = []
                br_on_commit = []

                missing_branch = set(self.branch_next_commit) - self.branch_treated
                for b in missing_branch:
                    self._handle_new_branch_and_draw(b)

                for branch, idx in self.branch_draw_index.items():
                    if self.branch_next_commit[branch] == commit:
                        br_idx.append(idx)
                        br_on_commit.append(branch)
                current_index = self.branch_draw_index[branch_to_draw]
                if current_index not in br_idx:
                    br_idx.append(current_index)
                    br_on_commit.append(branch_to_draw)

                self._draw_branching(
                    len(self.branch_draw_index),
                    *br_idx
                )

                branch_root = self._update_draw_index_after_branching(*br_on_commit)
                commit_draw_index = self.branch_draw_index[branch_root]
                self._draw_commit_or_tag(commit, commit_draw_index, commit_data)
                break

        for graph_holder in (
                self.graph_holder_tags,
                self.graph_holder_branch,
                self.graph_holder_commits):
            graph_holder.flush_buffer()

        return GraphData(
            graph_commit_item_list=self.graph_holder_commits.graph_data_item_list,
            graph_branch_item_list=self.graph_holder_branch.graph_data_item_list,
            graph_tag_item_list=self.graph_holder_tags.graph_data_item_list
        )

    def _resolve_branching_commits(self):
        _commits = {}
        for commit, commit_data in self.tree_commits.items():
            parent_commit = commit_data["parent"]
            if parent_commit not in _commits:
                _commits[parent_commit] = 1
            else:
                _commits[parent_commit] += 1
        for commit in self.tree_branches.values():
            if commit in _commits:
                _commits[commit] += 1
        for commit, number_of_children in _commits.items():
            if number_of_children > 1:
                self.branching_commits[commit] = number_of_children

    def _init_branch_next_date_and_branch_next_commit(self):
        for branch, commit in self.tree_branches.items():
            self.branch_next_commit[branch] = commit
            self.branch_next_date[branch] = self.tree_commits[commit]["date"]

    def _update_next_branch(self):
        next_branch = None
        max_date = None
        for branch, date in self.branch_next_date.items():
            if not next_branch  or date > max_date and branch not in self.branch_treated:
                next_branch = branch
                max_date = date
        if next_branch is not None:
            self.next_branch = next_branch
            self.next_branch_date = max_date
            self.branch_next_date.pop(next_branch)
        else:
            self.next_branch = None
            self.next_branch_date = None

    def _add_branch_to_draw_index(self, branch):
        indexes = self.branch_draw_index.values()
        if not len(indexes):
            idx = 0
        else:
            idx = max(indexes) + 1
        self.branch_draw_index[branch] = idx
        self.branch_treated.add(branch)

    def _get_branch_to_draw(self):
        branch_to_draw = None
        branch_to_draw_date = None

        # 1 / getting branch with upper date from already registered branches.
        for branch in self.branch_draw_index:
            commit = self.branch_next_commit[branch]
            date = self.tree_commits[commit]["date"]
            if (branch_to_draw_date is None or date > branch_to_draw_date):
                branch_to_draw_date = date
                branch_to_draw = branch

        # 2 / checking if branch in next_branch buffer has upper date.
        if self.next_branch and self.next_branch_date > date:
            branch_to_draw = self.next_branch
            branch_to_draw_date = self.next_branch_date

        return branch_to_draw, branch_to_draw_date

    def _update_branching_commits_drawn(self, commit, branch):
        if commit not in self.branching_commits:
            return
        if commit not in self.branching_commits_rdy:
            self.branching_commits_rdy[commit] = {branch}
        else:
            self.branching_commits_rdy[commit].add(branch)

    def _check_is_branching_to_draw(self, commit):
        if commit not in self.branching_commits:
            return False
        required_branch_on_commits = self.branching_commits[commit]
        if len(self.branching_commits_rdy[commit]) == required_branch_on_commits:
            return True
        else:
            return False

    def _handle_new_branch_and_draw(self, branch):
        self._add_branch_to_draw_index(branch)
        self._update_next_branch()
        self._draw_tip_of_branch(
            branch,
            len(self.branch_draw_index),
            self.branch_draw_index[branch]
        )

    def _update_draw_index_after_branching(self, *branches):
        branch_root = None
        min_root_id = None

        # resloving which is the main branch and which are the branch to delete.
        branches_idx = []
        for b in branches:
            b_id = self.branch_draw_index[b]
            if branch_root is None or b_id < min_root_id:
                branch_root = b
                min_root_id = b_id
            branches_idx.append(b_id)
        branch_id_deleted = [br_id for br_id in branches_idx if br_id != min_root_id]

        # removing merged branches from index.
        for b in branches:
            if b != branch_root:
                self.branch_draw_index.pop(b)

        # updating index of remaining branhces.
        for b in self.branch_draw_index.keys():
            b_id = self.branch_draw_index[b]
            deleted_branch_before_b_number = len([
                deleted_id for deleted_id in branch_id_deleted
                if deleted_id < b_id
            ])
            if b != branch_root:
                self.branch_draw_index[b] = self.branch_draw_index[b] - deleted_branch_before_b_number
        return branch_root

    # UPDATES LINES DRAWN FUNC -----------------------------------------------

    def _draw_tip_of_branch(self, branch_name, branch_number, branch_id):
        lines = graph_func.draw_tip_of_branch(branch_number, branch_id)
        for graph_holder in (
                self.graph_holder_tags,
                self.graph_holder_branch,
                self.graph_holder_commits):
            graph_holder.flush_buffer()
            graph_holder.add_buffer_lines(*lines)
            graph_holder.set_buffer(
                GraphDataBranch(lines=None, branch=branch_name)
            )

    def _draw_branching(self, branch_number, *branch_idx):
        lines = graph_func.draw_branching(branch_number, *branch_idx)
        for graph_holder in (
                self.graph_holder_tags,
                self.graph_holder_branch,
                self.graph_holder_commits):
            graph_holder.add_buffer_lines(*lines)

    def _draw_commit_or_tag(self, commit, commit_draw_index, commit_data):
        if commit not in self.tag_index:
            self._draw_commit(commit, commit_draw_index, commit_data)
        else:
            self._draw_tag(commit, commit_draw_index, commit_data)

    def _draw_commit(self, commit, commit_draw_index, commit_data):
        lines = graph_func.draw_commit(
            len(self.branch_draw_index),
            commit_draw_index
        )
        graph_holder = self.graph_holder_commits
        graph_holder.flush_buffer()
        graph_holder.add_buffer_lines(*lines)
        graph_holder.set_buffer(
            GraphDataCommit(
                lines=lines,
                commit_id=commit,
                commit_mess=commit_data["message"],
                user=commit_data["user"],
                date=commit_data["date"],
            )
        )

    def _draw_tag(self, commit, commit_draw_index, commit_data):
        lines = graph_func.draw_tag(
            len(self.branch_draw_index),
            commit_draw_index,
        )
        for graph_holder in (self.graph_holder_commits, self.graph_holder_tags):
            graph_holder.flush_buffer()
            graph_holder.add_buffer_lines(*lines)
            graph_holder.set_buffer(
                GraphDataTags(
                    lines=lines,
                    commit_id=commit,
                    commit_mess=commit_data["message"],
                    user=commit_data["user"],
                    date=commit_data["date"],
                    *self.tag_index[commit]
                )
            )
