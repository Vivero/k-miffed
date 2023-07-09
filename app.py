from ksp_interface import KspInterface, VesselAttitude, VesselOrbitalParameters
from mmap_interface import MemMapInterface
import time

from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Footer, Header, Input, Label, Static, TextLog

class KmiffedApp(App):
    #
    # Textual Properties
    #
    CSS_PATH = "main.css"
    TITLE = "Flight Computer"
    SUB_TITLE = "no connection"

    #
    # Constants
    #
    __KRPC_MONITOR_THREAD_INTERVAL_S = 0.0333333 # 30 Hz
    __NUM_PANELS = 4

    #
    # Types
    #
    class SetKrpcStatusMsg(Message):
        """Set KRPC status string message."""
        def __init__(self, status_str: str) -> None:
            self.status_str = status_str
            super().__init__()

    class SetOrbitalParametersMsg(Message):
        """Set orbital parameters message."""
        def __init__(self, period: float, tta: float, ttp: float) -> None:
            self.orbital_period = period
            self.time_to_apoapsis = tta
            self.time_to_periapsis = ttp
            super().__init__()

    #
    # Constructor
    #
    def __init__(self, krpc: KspInterface, mem_map: MemMapInterface):
        super().__init__()
        self.krpc = krpc
        self.mem_map = mem_map
        self.is_krpc_terminated = False
        self.selected_panel_idx = 0
        self.debug_counter = 0

    #
    # Public Methods
    #
    def compose(self) -> ComposeResult:
        # Start the KRPC Monitoring thread
        self._krpc_monitor_thread()

        with Container(id="main-container"):
            with Container(classes="panel", id="panel-orbital"):
                yield Label("Orbital Period", classes="table-field-name")
                yield Label("10", classes="table-field-value", id="field-value-orbital-period")
                yield Label("Time to Apoapsis", classes="table-field-name")
                yield Label("100", classes="table-field-value", id="field-value-orbital-tta")
                yield Label("Time to Periapsis", classes="table-field-name")
                yield Label("200", classes="table-field-value", id="field-value-orbital-ttp")
            with Vertical(classes="panel"):
                yield Static("Two")
            with Vertical(classes="panel"):
                yield Static("Three")
            with Vertical(classes="panel"):
                yield Static("Four")
            with Container(id="overlay-container"):
                yield TextLog(id="info-log", highlight=True, markup=True, wrap=True)

        yield Footer()
        yield Header(show_clock=True)

    #
    # Event Handlers
    #
    def on_ready(self) -> None:
        self.info_log_widget = self.query_one("#info-log")
        self.overlay_container_widget = self.query_one("#overlay-container")
        self.overlay_container_widget.border_title = "Info Log"

        # assign titles to panels
        panel_titles = ["Orbital Parameters", "Maneuvers", "Environment", "Subsystem Controls"]
        panels = self.query("#main-container > .panel")
        panel_idx = 0
        for panel in panels:
            # set the title
            if panel_idx < len(panel_titles):
                panel.border_title = panel_titles[panel_idx]
            panel_idx += 1

        # update selected panel style
        self._set_selected_panel_style()

    def on_key(self, event: events.Key) -> None:
        if event.key == 'l':
            if self.overlay_container_widget.styles.display == "none":
                self.overlay_container_widget.styles.display = "block"
            else:
                self.overlay_container_widget.styles.display = "none"

        elif event.key == 'i':
            self.info_log_widget.scroll_up()

        elif event.key == 'k':
            self.info_log_widget.scroll_down()

        elif event.key == 'o':
            self.debug_counter += 1
            self.info_log_widget.write("Test Counter: {0}".format(self.debug_counter))

        elif event.key == 'a':
            self.selected_panel_idx -= 1
            if self.selected_panel_idx < 0:
                self.selected_panel_idx = self.__NUM_PANELS - 1
            self._set_selected_panel_style()

        elif event.key == 'd':
            self.selected_panel_idx += 1
            if self.selected_panel_idx >= self.__NUM_PANELS:
                self.selected_panel_idx = 0
            self._set_selected_panel_style()

    def on_unmount(self) -> None:
        self.is_krpc_terminated = True

    #
    # Message Handlers
    #
    def on_kmiffed_app_set_krpc_status_msg(self, message: SetKrpcStatusMsg) -> None:
        self.sub_title = message.status_str

    def on_kmiffed_app_set_orbital_parameters_msg(self, message: SetOrbitalParametersMsg) -> None:
        label = self.query_one("#field-value-orbital-period", Label)
        label.update(KmiffedApp._format_time(message.orbital_period, False))
        label = self.query_one("#field-value-orbital-tta", Label)
        label.update(KmiffedApp._format_time(message.time_to_apoapsis, True))
        label = self.query_one("#field-value-orbital-ttp", Label)
        label.update(KmiffedApp._format_time(message.time_to_periapsis, True))

    #
    # Private Methods
    #
    def _set_selected_panel_style(self):
        panels = self.query("#main-container > .panel")
        panel_idx = 0
        for panel in panels:
            if panel_idx == self.selected_panel_idx:
                panel.add_class("panel-focused")
            else:
                panel.remove_class("panel-focused")
            panel_idx += 1

    @work(exclusive=True)
    def _krpc_monitor_thread(self) -> None:
        """Monitor our connection to the KRPC interface"""
        while not self.is_krpc_terminated:
            # Establish KRPC Connection
            self.krpc.setup_connection_if_needed()
            self.krpc.setup_data_streams_if_needed()

            # Get KRPC status info
            krpc_status_str = self.krpc.get_krpc_status()
            self.post_message(self.SetKrpcStatusMsg(krpc_status_str))

            # Get data to display on UI
            orbital_params = self.krpc.get_vessel_orbital_parameters()
            if orbital_params.bIsDataValid:
                self.post_message(self.SetOrbitalParametersMsg(
                    orbital_params.fPeriod,
                    orbital_params.fTimeToApoapsis,
                    orbital_params.fTimeToPeriapsis))

            # Get data for external interfaces
            vessel_attitude = self.krpc.get_vessel_attitude()
            self.mem_map.set_vessel_attitude(vessel_attitude)

            # Sleep till next frame
            time.sleep(self.__KRPC_MONITOR_THREAD_INTERVAL_S)

    @staticmethod
    def _format_time(seconds: float, is_showing_milliseconds: bool):
        days = int(seconds // (24 * 3600))
        seconds %= (24 * 3600)
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60

        formatted_time = ""
        if days > 0:
            formatted_time += f"{days}d "
        if hours > 0:
            formatted_time += f"{str(hours).zfill(2)}h "
        if minutes > 0:
            formatted_time += f"{str(minutes).zfill(2)}m "
        if is_showing_milliseconds:
            formatted_time += f"{seconds:6.3f}s"
        else:
            formatted_time += f"{seconds:2.0f}s"

        return formatted_time
