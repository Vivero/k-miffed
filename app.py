from flight_controller import FlightController
from ksp_interface import KspInterface
from ksp_types import VesselAttitude, VesselOrbitalParameters, VesselFlightControl, VesselFlightState
from mmap_interface import MemMapInterface
from panel import KMiffedPanel
from panel_control_program import PanelControlProgram
from panel_orbital_parameters import PanelOrbitalParameters
from panel_supplies import PanelSupplies
import time, threading
from datetime import datetime, timedelta

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
        # KSP interface via kRPC
        self.krpc = krpc
        self.is_krpc_terminated = False

        # External interface via shared memory
        self.mem_map = mem_map

        # UI controls
        self.selected_panel_idx = 0
        self.selected_panel_idx_prev = -1

        # Flight control members
        self.flight_control = VesselFlightControl(False, 0.0)
        self.flight_controller = FlightController()
        self.flight_control_lock = threading.Lock()
        self.flight_control_program = "manual"
        self.flight_control_program_data = 0.0

        # debugging tools
        self.debug_counter = 0

    #
    # Public Methods
    #
    def compose(self) -> ComposeResult:
        with Container(id="main-container"):
            yield PanelOrbitalParameters(classes="panel panel-format-table", id="panel-orbital")
            yield PanelSupplies(classes="panel panel-format-table", id="panel-supplies")
            yield PanelControlProgram(classes="panel panel-format-table", id="panel-program")
            yield KMiffedPanel("PlaceHolder", classes="panel")

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
        # panel_titles = ["Orbital Parameters", "Life Support", "Environment", "Subsystem Controls"]

        # store frequently used widgets
        self.panel_orbital_parameters = self.query_one("#panel-orbital", PanelOrbitalParameters)
        self.panel_supplies = self.query_one("#panel-supplies", PanelSupplies)
        self.panels = self.query("#main-container > .panel")

        # update selected panel style
        self._set_selected_panel()

        # Start the KRPC Monitoring thread
        self._krpc_monitor_thread()

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
            self.selected_panel_idx_prev = self.selected_panel_idx
            self.selected_panel_idx -= 1
            if self.selected_panel_idx < 0:
                self.selected_panel_idx = self.__NUM_PANELS - 1
            self._set_selected_panel()

        elif event.key == 'd':
            self.selected_panel_idx_prev = self.selected_panel_idx
            self.selected_panel_idx += 1
            if self.selected_panel_idx >= self.__NUM_PANELS:
                self.selected_panel_idx = 0
            self._set_selected_panel()

        elif event.key == 'w':
            self.panels[self.selected_panel_idx].on_panel_key_up()

        elif event.key == 's':
            self.panels[self.selected_panel_idx].on_panel_key_down()

        elif event.key == 'enter':
            self.panels[self.selected_panel_idx].on_panel_key_select()

    def on_unmount(self) -> None:
        self.is_krpc_terminated = True

    #
    # Message Handlers
    #
    def on_kmiffed_app_set_krpc_status_msg(self, message: SetKrpcStatusMsg) -> None:
        self.sub_title = message.status_str

    def on_panel_control_program_set_control_program_msg(self, message: PanelControlProgram.SetControlProgramMsg) -> None:
        self.info_log_widget.write("Control Program Activated: {0} {1}".format(message.control_program, message.program_data))
        self._set_flight_control_program(message.control_program, message.program_data)

    #
    # Private Methods
    #
    def _set_selected_panel(self):
        panel_idx = 0
        for panel in self.panels:
            if panel_idx == self.selected_panel_idx:
                panel.add_class("panel-focused")
                panel.on_panel_enter()
            else:
                panel.remove_class("panel-focused")

            if panel_idx == self.selected_panel_idx_prev:
                panel.on_panel_exit()
            panel_idx += 1

    def _set_flight_control_program(self, program: str, program_data: float) -> None:
        with self.flight_control_lock:
            self.flight_control_program = program
            self.flight_control_program_data = program_data

    def _get_flight_control_program(self) -> tuple:
        flight_control_program = "manual"
        flight_control_program_data = 0.0
        with self.flight_control_lock:
            flight_control_program = self.flight_control_program
            flight_control_program_data = self.flight_control_program_data
        return (flight_control_program, flight_control_program_data)

    @work(exclusive=True)
    def _krpc_monitor_thread(self) -> None:
        """Monitor our connection to the KRPC interface"""
        low_freq_loop_interval_ms = 5000
        low_freq_loop_time = datetime.now() - timedelta(milliseconds=low_freq_loop_interval_ms)

        while not self.is_krpc_terminated:
            current_timestamp = datetime.now()

            # Establish KRPC Connection
            self.krpc.setup_connection_if_needed()
            self.krpc.setup_data_streams_if_needed()

            # Get KRPC status info
            krpc_status_str = self.krpc.get_krpc_status()
            self.post_message(self.SetKrpcStatusMsg(krpc_status_str))

            # Get low-frequency-polled data for the UI
            if (current_timestamp - low_freq_loop_time) > timedelta(milliseconds=low_freq_loop_interval_ms):
                low_freq_loop_time = current_timestamp
                vessel_resources = self.krpc.get_vessel_resources()
                if vessel_resources.bIsDataValid:
                    self.panel_supplies.post_message(PanelSupplies.SetDataMsg(
                        vessel_resources.fWater,
                        vessel_resources.fWaterMax,
                        vessel_resources.fFood,
                        vessel_resources.fFoodMax,
                        vessel_resources.fOxygen,
                        vessel_resources.fOxygenMax,
                        vessel_resources.fAtmo,
                        vessel_resources.fAtmoMax,
                        vessel_resources.fWasteAtmo,
                        vessel_resources.fWasteAtmoMax))

            # Get data for external interfaces
            vessel_attitude = self.krpc.get_vessel_attitude()
            self.mem_map.set_vessel_attitude(vessel_attitude)

            # Execute flight controller
            vessel_flight_state = self.krpc.get_vessel_flight_state()
            print("\n\n vessel_flight_state: valid={0} Tmax={1} wght={2}".format(
                vessel_flight_state.bIsDataValid, vessel_flight_state.fThrustMax, vessel_flight_state.fWeight))
            (flight_ctrl_pgm, flight_ctrl_pgm_data) = self._get_flight_control_program()
            print("\n\n flight_ctrl_pgm: pgm={0} dat={1}".format(flight_ctrl_pgm, flight_ctrl_pgm_data))
            if vessel_flight_state.bIsDataValid:
                self.flight_control = self.flight_controller.execute(
                    flight_ctrl_pgm,
                    flight_ctrl_pgm_data,
                    vessel_flight_state)
                print("\n\n flight_control: use={0} throttle={1}".format(self.flight_control.bIsInputValid, self.flight_control.fThrottle))
            else:
                self.flight_control.bIsInputValid = False
            if self.flight_control.bIsInputValid:
                self.krpc.set_flight_controls(self.flight_control)

            # Get data to display on UI
            orbital_params = self.krpc.get_vessel_orbital_parameters()
            if orbital_params.bIsDataValid:
                self.panel_orbital_parameters.post_message(PanelOrbitalParameters.SetDataMsg(
                    orbital_params.sCelestialBodyName,
                    orbital_params.fPeriod,
                    orbital_params.fTimeToApoapsis,
                    orbital_params.fTimeToPeriapsis,
                    vessel_flight_state.fVerticalSpeed))

            # Sleep till next frame
            time.sleep(self.__KRPC_MONITOR_THREAD_INTERVAL_S)
