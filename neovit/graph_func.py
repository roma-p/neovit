
# -- BASIC DRAW FUNCTIONS -----------------------------------------------------


def draw_tree_basic(branch_number):
    return "| "*branch_number


def draw_tree_uncommit_changes(branch_number, branch_id):
    line = ""
    for i in range(branch_number):
        if i == branch_id:
            line += ": "
        else:
            line += "| "
    return line


def draw_tree_star(branch_number, branch_id, char="*"):
    line = "| "
    line_n_left  = branch_id
    line_n_right = branch_number - branch_id - 1
    return line * line_n_left + char + " " + line * line_n_right


def draw_tree_push_left(branch_number, branch_id):
    line_n_left = branch_id
    line_n_right = branch_number - branch_id - 1
    return "| " * line_n_left + "|/ " + "/ " * line_n_right


def draw_tree_split_left(branch_number, branch_id):
    line_n_left = branch_id
    line_n_right = branch_number - branch_id - 1
    line = "| "
    return line * line_n_left + "|/" + line * line_n_right

# -- DRAW EVENTS --------------------------------------------------------------


def draw_commit(branch_number, branch_id):
    lines = []
    lines.append(draw_tree_star(branch_number, branch_id))
    lines.append(draw_tree_basic(branch_number))
    lines.append(draw_tree_basic(branch_number))
    lines.append(draw_tree_basic(branch_number))
    return lines


def draw_tag(branch_number, branch_id):
    lines = []

    lines.append(draw_tree_star(branch_number, branch_id, "o"))
    lines.append(draw_tree_basic(branch_number))
    lines.append(draw_tree_basic(branch_number))
    lines.append(draw_tree_basic(branch_number))
    lines.append(draw_tree_basic(branch_number))
    return lines


def draw_branching(branch_number, *branches):

    br_root = min(branches)
    br_children  = sorted([b for b in branches if b != br_root], reverse=True)

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
            lines.append(draw_tree_push_left(branch_number - (i+1), split_idx))
            split_idx = split_idx - 1
            split_to_draw = split_to_draw - 1

        for j in range(split_to_draw):
            lines.append(draw_tree_split_left(branch_number - (i+1), split_idx))
            split_idx = split_idx - 1
    return lines


def draw_tip_of_branch(branch_number, branch_id):
    return [
        draw_tree_star(branch_number, branch_id, "O"),
        draw_tree_basic(branch_number)
    ]


def draw_uncommit_changes_on_branch(branch_number, branch_id):
    return [
        draw_tree_star(branch_number, branch_id, "O"),
        draw_tree_uncommit_changes(branch_number, branch_id),
        draw_tree_uncommit_changes(branch_number, branch_id)
    ]
