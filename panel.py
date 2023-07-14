from textual.containers import Container

class KMiffedPanel(Container):
    #
    # Constants
    #
    PANEL_TITLE = ""

    #
    # Constructor
    #
    def __init__(self, panel_title, classes=None, id=None):
        self.PANEL_TITLE = panel_title
        super().__init__(classes=classes, id=id)

    #
    # Event Handlers
    #
    def on_mount(self) -> None:
        # assign title to panel
        self.border_title = self.PANEL_TITLE

    def on_panel_enter(self) -> None:
        pass

    def on_panel_exit(self) -> None:
        pass

    def on_panel_key_up(self) -> None:
        pass

    def on_panel_key_down(self) -> None:
        pass

    def on_panel_key_select(self) -> None:
        pass
