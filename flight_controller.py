from datetime import datetime, timedelta
from ksp_types import VesselFlightControl, VesselFlightState
from pid_controller import PidController

class FlightController:
    #
    # Constants
    #

    #
    # Constructor
    #
    def __init__(self):
        self.vertical_speed_ctrl = PidController(kp=0.181, ki=0.09, kd=0.005, output_min=0.0, output_max=1.0, set_point=0.0)
        self.altitude_ctrl = PidController(kp=0.2, ki=0.005, kd=0.005, output_min=-5.0, output_max=5.0, set_point=85.0)

    #
    # Public Methods
    #
    def execute(self, control_program: str, program_data: float, state: VesselFlightState) -> VesselFlightControl:
        control = VesselFlightControl(False, 0.0)
        if control_program == "vspeed":
            if state.fThrustMax > 0.0:
                # set control gains
                ku = state.fWeight / state.fThrustMax
                self.vertical_speed_ctrl.kp = ku * 0.70
                self.vertical_speed_ctrl.ki = ku / 3.0
                self.vertical_speed_ctrl.kd = ku / 50.0

                self.vertical_speed_ctrl.set_point = program_data
                control.fThrottle = self.vertical_speed_ctrl.update(state.fVerticalSpeed)
                control.bIsInputValid = True
        return control

    #
    # Private Methods
    #
