from itertools import cycle

from neovit import graph_func
from rich import print as rprint
from rich.text import Text, TextType
from rich.console import Console
import unittest


class TestGraphFunc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.console = Console()

    @classmethod
    def rpint(cls, text):
        cls.console.print("")
        cls.console.print(text)

    @classmethod
    def rprint_lines(cls, lines):
        cls.console.print("")
        for line in lines:
            cls.console.print(line)

    def pick_colors(self, number):
        COLORS = cycle((
            "red",
            "blue",
            "green",
            "magenta",
            "yellow",
            "cyan",
        ))
        ret = []
        for i in range(number):
            ret.append(next(COLORS))
        return tuple(ret)

    def _test_tree_basic(self):
        ret = graph_func.draw_tree_basic(4, self.pick_colors(4))
        self.rpint(ret)

    def _test_draw_tree_star(self):
        ret = graph_func.draw_tree_star(3, 1, self.pick_colors(3))
        self.rpint(ret)

    def _test_tree_push_left(self):
        ret = graph_func.draw_tree_push_left(4, 2, self.pick_colors(5))
        self.rpint(ret)

    def _test_tree_split_left(self):
        ret = graph_func.draw_tree_split_left(4, 2, self.pick_colors(5))
        self.rpint(ret)

    def _test_draw_commit(self):
        ret = graph_func.draw_commit(3, 1, self.pick_colors(3))
        self.rprint_lines(ret)

    def _test_draw_tag(self):
        ret = graph_func.draw_tag(3, 1, self.pick_colors(3))
        self.rprint_lines(ret)

    def test_draw_branching_new(self):
        self.rprint_lines(graph_func.draw_branching(5, self.pick_colors(5), 1, 0, 3))
        self.rprint_lines(graph_func.draw_branching(7, self.pick_colors(7), 0, 1, 4))
        self.rprint_lines(graph_func.draw_branching(6, self.pick_colors(6), 3, 5, 4))
        self.rprint_lines(graph_func.draw_branching(7, self.pick_colors(7), 0, 1, 2, 5))
        self.rprint_lines(graph_func.draw_branching(4, self.pick_colors(4), 0, 1, 2, 3))
        self.rprint_lines(graph_func.draw_branching(7, self.pick_colors(7), 1, 2, 4, 6))
