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
        self.vertical_speed_ctrl = PidController(kp=0.181, ki=0.09, kd=0.005, output_min=0.001, output_max=1.0, set_point=0.0)
        # self.altitude_ctrl = PidController(kp=0.2, ki=0.005, kd=0.005, output_min=-5.0, output_max=5.0, set_point=85.0)
        self.pitch_ctrl = PidController(kp=0.1, ki=0.0, kd=0.0, output_min=-1.0, output_max=1.0, set_point=0.0)
        self.yaw_ctrl = PidController(kp=0.1, ki=0.0, kd=0.0, output_min=-1.0, output_max=1.0, set_point=0.0)
        self.fwd_ctrl = PidController(kp=1, ki=0.0, kd=0.0, output_min=-1.1, output_max=1.1, set_point=0.0)
        self.lat_ctrl = PidController(kp=1, ki=0.0, kd=0.0, output_min=-1.1, output_max=1.1, set_point=0.0)

        self.print_counter = 0

    #
    # Public Methods
    #
    def execute(self, control_program: str, program_data: float, state: VesselFlightState) -> VesselFlightControl:
        control = VesselFlightControl(False, 0.0, 0.0, 0.0)
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

        elif control_program == "attitude":
        #else:
            if state.fThrustMax > 0.0:
                # set control gains
                ku = state.fWeight / state.fThrustMax
                self.vertical_speed_ctrl.kp = ku * 0.70
                self.vertical_speed_ctrl.ki = ku / 3.0
                self.vertical_speed_ctrl.kd = ku / 50.0

                # null out the vertical speed
                self.vertical_speed_ctrl.set_point = program_data
                control.fThrottle = self.vertical_speed_ctrl.update(state.fVerticalSpeed)
                control.bIsInputValid = True

            # null out forward speed
            self.fwd_ctrl.set_point = 0.0
            ku = 0.01
            self.fwd_ctrl.kp = ku * 0.70
            self.fwd_ctrl.ki = 0
            self.fwd_ctrl.kd = 0
            target_pitch_speed = self.fwd_ctrl.update(state.fForwardSpeed)

            # null out lateral speed
            self.lat_ctrl.set_point = 0.0
            self.lat_ctrl.kp = ku * 7.70
            self.lat_ctrl.ki = 0
            self.lat_ctrl.kd = 0
            target_yaw_speed = -self.lat_ctrl.update(state.fLateralSpeed)

            # self.pitch_ctrl.set_point = 0.0
            self.pitch_ctrl.set_point = target_pitch_speed
            # self.pitch_ctrl.set_point = program_data
            ku = state.fPitchMomentOfInertia / state.fPitchTorqueMax * 10 if state.fPitchTorqueMax > 0.0 else 1.0
            self.pitch_ctrl.kp = ku * 0.70
            self.pitch_ctrl.ki = 0 # ku / 3.0
            self.pitch_ctrl.kd = 0 # ku / 50.0
            control.fPitch = -self.pitch_ctrl.update(state.fPitchSpeed)

            # self.yaw_ctrl.set_point = 0.0
            self.yaw_ctrl.set_point = target_yaw_speed
            ku = state.fYawMomentOfInertia / state.fYawTorqueMax * 10 if state.fYawTorqueMax > 0.0 else 1.0
            self.yaw_ctrl.kp = ku * 0.70
            self.yaw_ctrl.ki = 0 # ku / 3.0
            self.yaw_ctrl.kd = 0 # ku / 50.0
            control.fYaw = -self.yaw_ctrl.update(state.fYawSpeed)

            self.print_counter += 1
            if self.print_counter > 4:
                # print("Controls: Pitch={0:7.3f}   Yaw={1:7.3f}".format(control.fPitch, control.fYaw))
                print("Controls: Pitch={0:7.3f}   TgtPitchSpd={1:7.3f}   Yaw={2:7.3f}   TgtYawSpd={3:7.3f}".format(
                    control.fPitch, target_pitch_speed, control.fYaw, target_yaw_speed))
                self.print_counter = 0

            control.bIsInputValid = True

        return control

    #
    # Private Methods
    #
