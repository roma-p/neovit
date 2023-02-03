from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Tree, Button



class NeoVit(App):
    CSS_PATH = "neovit.css"

    BINDINGS = [
        ("r", "refresh", "refresh view from current metadata")
    ]

    

    def compose(self) -> ComposeResult:
        yield Header("neovit")
        yield TopBandWidget("band", classes="box")
        yield ControlView("control", classes="box", id="two")
        yield RepoView("repo", classes="box", id="repoView")

    def action_refresh(self) -> None :
        tree = self.query_one(DistantRepoView)
        tree.root.add("jinx", expand=True)

class TopBandWidget(Static):
    pass


class RepoView(Static):
    def compose(self):
        yield DistantRepoView("RepoName", classes="box")
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

class DistantRepoView(Tree):

#    def compose(self):
#        self.root.expand()
#        package = self.root.add("Jinx", expand=True)
#        package.add_leaf("mod")
#        package.add_leaf("rigg")
#        package.add_leaf("surf")
#        return set()

    def NodeSelected(self):
        print("prout")

class AssetView(Static):
    def compose(self):
        yield GraphRow()
        yield GraphRow()
        yield GraphRow()
        yield GraphRow()

if __name__ == "__main__":
    app = NeoVit()
    app.run()
