from panel import KMiffedPanel
from util import format_time

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Label

class PanelOrbitalParameters(KMiffedPanel):
    #
    # Types
    #
    class SetDataMsg(Message):
        """Set widget data message."""
        def __init__(self, cbody_name: str, period: float, tta: float, ttp: float, vspeed: float) -> None:
            self.cbody_name = cbody_name
            self.orbital_period = period
            self.time_to_apoapsis = tta
            self.time_to_periapsis = ttp
            self.vertical_speed = vspeed
            super().__init__()

    #
    # Constructor
    #
    def __init__(self, classes=None, id=None):
        super().__init__("Orbital Parameters", classes=classes, id=id)

    #
    # Public Methods
    #
    def compose(self) -> ComposeResult:
        yield Label("Celestial Body", classes="table-field-name")
        yield Label("N/A", classes="table-field-value", id="field-value-cbody-name")
        yield Label("Orbital Period", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-orbital-period")
        yield Label("Time to Apoapsis", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-orbital-tta")
        yield Label("Time to Periapsis", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-orbital-ttp")
        yield Label("Vertical Speed", classes="table-field-name")
        yield Label("0", classes="table-field-value", id="field-value-vertical-speed")

    def set_data(self,
                 cbody_name: str,
                 orbital_period: float,
                 time_to_apoapsis: float,
                 time_to_periapsis: float,
                 vertical_speed: float) -> None:
        self.label_cbody_name.update(cbody_name)
        self.label_orbital_period.update(format_time(orbital_period, False))
        self.label_orbital_tta.update(format_time(time_to_apoapsis, True))
        self.label_orbital_ttp.update(format_time(time_to_periapsis, True))
        self.label_vertical_speed.update(format(vertical_speed, ".2f"))

    #
    # Event Handlers
    #
    def on_mount(self) -> None:
        # store frequently used widgets
        self.label_cbody_name = self.query_one("#field-value-cbody-name", Label)
        self.label_orbital_period = self.query_one("#field-value-orbital-period", Label)
        self.label_orbital_tta = self.query_one("#field-value-orbital-tta", Label)
        self.label_orbital_ttp = self.query_one("#field-value-orbital-ttp", Label)
        self.label_vertical_speed = self.query_one("#field-value-vertical-speed", Label)

        super().on_mount()

    #
    # Message Handlers
    #
    def on_panel_orbital_parameters_set_data_msg(self, message: SetDataMsg) -> None:
        self.set_data(
            message.cbody_name,
            message.orbital_period,
            message.time_to_apoapsis,
            message.time_to_periapsis,
            message.vertical_speed)
