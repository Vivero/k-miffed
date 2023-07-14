from panel import KMiffedPanel

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Label

class PanelControlProgram(KMiffedPanel):
    #
    # Types
    #
    class SetDataMsg(Message):
        """Set widget data message."""
        def __init__(self) -> None:
            super().__init__()

    class SetControlProgramMsg(Message):
        def __init__(self, program: str, program_data: float) -> None:
            self.control_program = program
            self.program_data = program_data
            super().__init__()

    #
    # Constructor
    #
    def __init__(self, classes=None, id=None):
        self.hovered_item_idx = -1
        self.hovered_item_idx_last = 0
        self.selected_item_idx = 0
        self.programs = [
            "manual",
            "vspeed",
            "altitude",
        ]
        super().__init__("Program", classes=classes, id=id)

    #
    # Public Methods
    #
    def compose(self) -> ComposeResult:
        yield Label("Manual", classes="item-label")
        yield Label("Maintain VSpeed", classes="item-label")
        yield Label("Maintain Altitude", classes="item-label")

    def set_data(self) -> None:
        pass

    def on_panel_enter(self) -> None:
        KMiffedPanel.on_panel_enter(self)
        self.hovered_item_idx = self.hovered_item_idx_last
        self._update_items()

    def on_panel_exit(self) -> None:
        KMiffedPanel.on_panel_exit(self)
        self.hovered_item_idx = -1
        self._update_items()

    def on_panel_key_down(self) -> None:
        KMiffedPanel.on_panel_key_down(self)
        self.hovered_item_idx += 1
        if self.hovered_item_idx >= len(self.items):
            self.hovered_item_idx = 0
        self.hovered_item_idx_last = self.hovered_item_idx
        self._update_items()

    def on_panel_key_up(self) -> None:
        KMiffedPanel.on_panel_key_up(self)
        self.hovered_item_idx -= 1
        if self.hovered_item_idx < 0:
            self.hovered_item_idx = len(self.items) - 1
        self.hovered_item_idx_last = self.hovered_item_idx
        self._update_items()

    def on_panel_key_select(self) -> None:
        KMiffedPanel.on_panel_key_select(self)
        self.selected_item_idx = self.hovered_item_idx
        self._update_items()

        # self.post_message(self.SetControlProgramMsg(self.programs[self.selected_item_idx], 10.0))
        if self.selected_item_idx == 0:
            self.post_message(self.SetControlProgramMsg("manual", 0.0))
        elif self.selected_item_idx == 1:
            self.post_message(self.SetControlProgramMsg("vspeed", 5.0))
        elif self.selected_item_idx == 2:
            self.post_message(self.SetControlProgramMsg("vspeed", -3.0))

    #
    # Event Handlers
    #
    def on_mount(self) -> None:
        # assign title to panel
        self.border_title = self.PANEL_TITLE
        self.items = self.query(".item-label")
        self._update_items()
        super().on_mount()
    #
    # Message Handlers
    #
    def on_panel_control_program_set_data_msg(self, message: SetDataMsg) -> None:
        self.set_data()

    #
    # Private Methods
    #
    def _update_items(self):
        item_idx = 0
        for item in self.items:
            if item_idx == self.selected_item_idx:
                item.add_class("item-label-selected")
                item.remove_class("item-label-hovered")
            elif item_idx == self.hovered_item_idx:
                item.add_class("item-label-hovered")
            else:
                item.remove_class("item-label-selected")
                item.remove_class("item-label-hovered")
            item_idx += 1
