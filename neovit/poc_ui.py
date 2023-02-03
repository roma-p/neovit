from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Button



class NeoVitApp(App):

    CSS_PATH = "neovit.css"

    def compose(self) -> ComposeResult:
        self.dark = True
        yield Header()
        yield Footer()
        yield Container(NeoVitMainContainer())

class NeoVitMainContainer(Static):
    def compose(self) -> ComposeResult:
        yield LeftContainer()
        yield CommandsContainer()

class CommandsContainer(Static):
    def compose(self) -> ComposeResult:
        yield Button("ta mere")

class LeftContainer(Static):
    def compose(self) -> ComposeResult:
        yield CommandLineContainer()
        yield RepoViewContainer()

class CommandLineContainer(Static):
    def compose(self) -> ComposeResult:
        yield Button("prout")
    pass

class RepoViewContainer(Static):
    def compose(self) -> ComposeResult:
        yield Button("prout")
        #yield OriginViewContainer()

class OriginViewContainer(Static):
    def compose(self) -> ComposeResult:
        yield OriginRepoTreeView()
        yield OriginAssetTreeView()


class OriginRepoTreeView(Static):
    pass


class OriginAssetTreeView(Static):
    pass
NeoVitApp().run()
