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
        def __init__(self,
                     cbody_name: str,
                     orbital_period: float,
                     time_to_apoapsis: float,
                     time_to_periapsis: float,
                     vertical_speed: float,
                     forward_speed: float,
                     lateral_speed: float,
                     pitch_speed: float,
                     pitch_torque_max: float,
                     pitch_moi: float,
                     yaw_speed: float,
                     yaw_torque_max: float,
                     yaw_moi: float) -> None:
            self.cbody_name = cbody_name
            self.orbital_period = orbital_period
            self.time_to_apoapsis = time_to_apoapsis
            self.time_to_periapsis = time_to_periapsis
            self.vertical_speed = vertical_speed
            self.forward_speed = forward_speed
            self.lateral_speed = lateral_speed
            self.pitch_speed = pitch_speed
            self.pitch_torque_max = pitch_torque_max
            self.pitch_moi = pitch_moi
            self.yaw_speed = yaw_speed
            self.yaw_torque_max = yaw_torque_max
            self.yaw_moi = yaw_moi
            super().__init__()

    #
    # Constructor
    #
    def __init__(self, classes=None, id=None):
        self.table_entries = {
            "cbody-name": "Celestial Body",
            "orbital-period": "Orbital Period",
            "orbital-tta": "Time to Apoapsis",
            "orbital-ttp": "Time to Periapsis",
            "vertical-speed": "Vertical Speed",
            "forward-speed": "Forward Speed",
            "lateral-speed": "Lateral Speed",
            "pitch-speed": "Pitch Speed",
            "pitch-torque-max": "Pitch Max Torque",
            "pitch-moi": "Pitch MoI",
            "yaw-speed": "Yaw Speed",
            "yaw-torque-max": "Yaw Max Torque",
            "yaw-moi": "Yaw MoI",
        }
        super().__init__("Orbital Parameters", classes=classes, id=id)

    #
    # Public Methods
    #
    def compose(self) -> ComposeResult:
        for id, title in self.table_entries.items():
            yield Label(title, classes="table-field-name")
            yield Label("", classes="table-field-value", id="field-value-{0}".format(id))

    #
    # Event Handlers
    #
    def on_mount(self) -> None:
        # store frequently used widgets
        self.field_value_widgets = {}
        for id, title in self.table_entries.items():
            self.field_value_widgets[id] = self.query_one("#field-value-{0}".format(id), Label)

        super().on_mount()

    #
    # Message Handlers
    #
    def on_panel_orbital_parameters_set_data_msg(self, message: SetDataMsg) -> None:
        self.field_value_widgets["cbody-name"].update(message.cbody_name)
        self.field_value_widgets["orbital-period"].update(format_time(message.orbital_period, False))
        self.field_value_widgets["orbital-tta"].update(format_time(message.time_to_apoapsis, True))
        self.field_value_widgets["orbital-ttp"].update(format_time(message.time_to_periapsis, True))
        self.field_value_widgets["vertical-speed"].update(format(message.vertical_speed, ".2f"))
        self.field_value_widgets["forward-speed"].update(format(message.forward_speed, ".2f"))
        self.field_value_widgets["lateral-speed"].update(format(message.lateral_speed, ".2f"))
        self.field_value_widgets["pitch-speed"].update(format(message.pitch_speed, ".2f"))
        self.field_value_widgets["pitch-torque-max"].update(format(message.pitch_torque_max, ".2f"))
        self.field_value_widgets["pitch-moi"].update(format(message.pitch_moi, ".2f"))
        self.field_value_widgets["yaw-speed"].update(format(message.yaw_speed, ".2f"))
        self.field_value_widgets["yaw-torque-max"].update(format(message.yaw_torque_max, ".2f"))
        self.field_value_widgets["yaw-moi"].update(format(message.yaw_moi, ".2f"))
