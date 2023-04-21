from rich.text import Text
from collections import namedtuple

# -- PUBLIC ------------------------------------------------------------------

LineBuffer = namedtuple("LineBuffer", ["graph_line_buffer", "color_by_branch"])


def draw_commit(branch_number, branch_id, rich_color_by_branch):
    lines = []
    lines.append(_draw_tree_star(branch_number, branch_id, rich_color_by_branch))
    lines.append(_draw_tree_basic(branch_number, rich_color_by_branch))
    lines.append(_draw_tree_basic(branch_number, rich_color_by_branch))
    lines.append(_draw_tree_basic(branch_number, rich_color_by_branch))
    return lines


def draw_tag(branch_number, branch_id, rich_color_by_branch):
    lines = []

    lines.append(_draw_tree_star(branch_number, branch_id, rich_color_by_branch, "o"))

    lines.append(_draw_tree_basic(branch_number, rich_color_by_branch))
    lines.append(_draw_tree_basic(branch_number, rich_color_by_branch))
    lines.append(_draw_tree_basic(branch_number, rich_color_by_branch))
    lines.append(_draw_tree_basic(branch_number, rich_color_by_branch))
    return lines


def draw_branching(
        branch_number,
        rich_color_by_branch,
        *branches):

    color_by_branch = rich_color_by_branch

    br_root = min(branches)
    br_children = sorted([b for b in branches if b != br_root], reverse=True)

    lines = list()

    split_idx = br_children[0] - 1

    for i in range(len(br_children)):

        br_0 = br_children[i]

        if i+1 < len(br_children):
            br_1 = br_children[i+1]
        else:
            br_1 = None

        if br_1 is not None:
            split_to_draw = br_0 - br_1
        else:
            split_to_draw = br_0 - br_root

        if br_0 + 1 < branch_number:
            lines.append(_draw_tree_push_left(
                branch_number - (i+1),
                split_idx,
                color_by_branch
            ))
            color_by_branch = _swap_tuple_at_index(color_by_branch, split_idx)
            split_idx = split_idx - 1
            split_to_draw = split_to_draw - 1

        for j in range(split_to_draw):
            lines.append(
                _draw_tree_split_left(
                    branch_number - (i+1),
                    split_idx,
                    color_by_branch
                ))
            color_by_branch = _swap_tuple_at_index(color_by_branch, split_idx)
            split_idx = split_idx - 1
        color_by_branch = _pop_tuple_at_index(color_by_branch, split_idx + 1)
    return lines, color_by_branch


def draw_tip_of_branch(branch_number, branch_id, rich_color_by_branch):
    return [
        _draw_tree_star(branch_number, branch_id, rich_color_by_branch, "O"),
        _draw_tree_basic(branch_number, rich_color_by_branch)
    ]


def draw_tree_uncommit_changes(branch_number, branch_id, rich_color_by_branch):
    return _draw_tree_star(branch_number, branch_id, ":")


def draw_uncommit_changes_on_branch(branch_number, branch_id, rich_color_by_branch):
    return [
        _draw_tree_star(branch_number, branch_id, rich_color_by_branch, "O"),
        draw_tree_uncommit_changes(branch_number, branch_id, rich_color_by_branch),
        draw_tree_uncommit_changes(branch_number, branch_id, rich_color_by_branch)
    ]


def convert_line_buffers_to_rich_text(line_buffer_list):
    text = Text()
    for line_buffer in line_buffer_list:
        item_list, rich_color_list = line_buffer
        for i in range(len(item_list)):
            if i < len(rich_color_list):
                color = rich_color_list[i]
                if color is not None:
                    text.append(item_list[i], style=color)
                else:
                    text.append(item_list[i])
            else:
                text.append(item_list[i])
        text.append("\n")
    return text

# -- PRIVATE ------------------------------------------------------------------

# -- basic draw functions -----------------------------------------------------


def _draw_tree_basic(branch_number, rich_color_by_branch):
    return LineBuffer(["| "]*branch_number, rich_color_by_branch)


def _draw_tree_star(branch_number, branch_id, rich_color_by_branch, char="*"):
    line = "| "
    line_n_left = branch_id
    line_n_right = branch_number - branch_id - 1
    item_list = [line] * line_n_left + [char + " "] + [line] * line_n_right
    return LineBuffer(item_list, rich_color_by_branch)


def _draw_tree_push_left(branch_number, branch_id, rich_color_by_branch):
    line_n_left = branch_id
    line_n_right = branch_number - branch_id - 1
    item_list = ["| "] * line_n_left + ["|"] + ["/ "] + ["/ "] * line_n_right
    return LineBuffer(item_list, rich_color_by_branch)


def _draw_tree_split_left(branch_number, branch_id, rich_color_by_branch):
    line_n_left = branch_id
    line_n_right = branch_number - branch_id - 1
    line = "| "
    item_list = [line] * line_n_left + ["|"] + ["/"] + [line] * line_n_right
    return LineBuffer(item_list, rich_color_by_branch)

# -- utils --------------------------------------------------------------------


def _enrich_graph_line(item_list, rich_color_list):
    text = Text()
    for i in range(len(item_list)):
        if i < len(rich_color_list):
            color = rich_color_list[i]
            if color is not None:
                text.append(item_list[i], style=color)
            else:
                text.append(item_list[i])
        else:
            text.append(item_list[i])
    return text


def _swap_tuple_at_index(iterable, idx):
    # swap iterable[idx] et iterable[idx+1]
    iterable = list(iterable)
    _tmp = iterable[idx]
    iterable[idx] = iterable[idx+1]
    iterable[idx+1] = _tmp
    return tuple(iterable)


def _pop_tuple_at_index(iterable, idx):
    iterable = list(iterable)
    iterable.pop(idx)
    return tuple(iterable)
