from datetime import datetime, timedelta
import krpc, math
import numpy as np
from ksp_types import VesselAttitude, VesselFlightControl, VesselFlightState, VesselOrbitalParameters, VesselResources
from pyquaternion import Quaternion
from util import project_a_onto_b, project_vector_a_onto_plane_b, vector_normalize

class KspInterface:
    #
    # Constants
    #
    MAX_RETRY_INTERVAL_MS = 5000

    #
    # Constructor
    #
    def __init__(self, ip_address, rpc_port, stream_port):
        self.ip_address = ip_address
        self.rpc_port = rpc_port
        self.stream_port = stream_port
        self.is_connected = False
        self.is_data_streaming = False
        self.last_connect_time = datetime.now()
        self.last_data_setup_time = datetime.now()
        self.retry_interval_ms = 100

    #
    # Public Methods
    #
    def init_connection(self) -> bool:
        if self.is_connected:
            return True

        try:
            print("Attempting to connect KRPC...")
            self.last_connect_time = datetime.now()
            self.krpc_connection = krpc.connect(
                name="Kockpit",
                address=self.ip_address,
                rpc_port=self.rpc_port,
                stream_port=self.stream_port)
            self.is_connected = True
            self.retry_interval_ms = 100

            # self.__execute_debugging_tools()

        except Exception as e:
            self.is_connected = False
            print("Failed to connect KRPC interface")
            print("Exception type    : ", type(e).__name__)
            print("Exception message : ", str(e))

        if not self.is_connected:
            return self.is_connected

        return self.is_connected

    def deinit_connection(self) -> None:
        if not self.is_connected:
            return
        self.krpc_connection.close()

    def setup_connection_if_needed(self) -> None:
        if self.is_connected:
            return

        current_timestamp = datetime.now()
        time_since_last_connect = current_timestamp - self.last_connect_time
        if time_since_last_connect > timedelta(milliseconds=self.retry_interval_ms):
            is_success = self.init_connection()
            if not is_success:
                self.__increase_retry_interval()

    def setup_data_streams_if_needed(self) -> None:
        if self.is_data_streaming or (not self.is_connected):
            return

        current_timestamp = datetime.now()
        time_since_last_data_setup = current_timestamp - self.last_data_setup_time
        if time_since_last_data_setup < timedelta(milliseconds=self.retry_interval_ms):
            return

        try:
            print("Setting up KRPC data streams...")
            self.last_data_setup_time = datetime.now()

            self.gravitational_constant = self.krpc_connection.space_center.g
            vessel = self.krpc_connection.space_center.active_vessel
            self.stream_vessel_orbit = self.krpc_connection.add_stream(getattr, vessel, 'orbit')
            vessel_flight = vessel.flight() # surface reference frame

            # Vessel attitude
            self.stream_heading = self.krpc_connection.add_stream(getattr, vessel_flight, 'heading')
            self.stream_pitch = self.krpc_connection.add_stream(getattr, vessel_flight, 'pitch')
            self.stream_roll = self.krpc_connection.add_stream(getattr, vessel_flight, 'roll')

            # Vessel flight state
            self.stream_situation = self.krpc_connection.add_stream(getattr, vessel, 'situation')
            self.stream_max_thrust = self.krpc_connection.add_stream(getattr, vessel, 'max_thrust')
            self.stream_mass = self.krpc_connection.add_stream(getattr, vessel, 'mass')
            self.stream_max_torque = self.krpc_connection.add_stream(getattr, vessel, 'available_torque')
            self.stream_moi = self.krpc_connection.add_stream(getattr, vessel, 'moment_of_inertia')

            # Vessel's orbital parameters
            # self.stream_orbital_period = self.krpc_connection.add_stream(getattr, vessel.orbit, 'period')
            # self.stream_time_to_apoapsis = self.krpc_connection.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
            # self.stream_time_to_periapsis = self.krpc_connection.add_stream(getattr, vessel.orbit, 'time_to_periapsis')

            # Visual debugging markers
            self.draw_vessel_pos_unit = self.krpc_connection.drawing.add_line((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), self.stream_vessel_orbit().body.reference_frame)
            self.draw_vessel_pos_unit.color = (0.0, 1.0, 0.0)
            self.draw_vessel_vel_unit = self.krpc_connection.drawing.add_line((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), self.stream_vessel_orbit().body.reference_frame)
            self.draw_vessel_vel_unit.color = (0.0, 0.0, 1.0)
            self.draw_vessel_srfvel_unit = self.krpc_connection.drawing.add_line((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), self.stream_vessel_orbit().body.reference_frame)
            self.draw_vessel_srfvel_unit.color = (1.0, 0.0, 0.0)
            self.draw_vessel_fwd_unit = self.krpc_connection.drawing.add_line((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), self.stream_vessel_orbit().body.reference_frame)
            self.draw_vessel_fwd_unit.color = (1.0, 0.6, 0.1)

            self.is_data_streaming = True
            self.retry_interval_ms = 100

        except Exception as e:
            print("Failed to setup KRPC data streams")
            print("Exception type    : ", type(e).__name__)
            print("Exception message : ", str(e))

            self.is_data_streaming = False
            self.__increase_retry_interval()

    def get_krpc_status(self) -> str:
        krpc_status = "no connection"

        if not self.is_connected:
            return krpc_status

        try:
            krpc_status = self.krpc_connection.krpc.get_status().version

        except ConnectionAbortedError as e:
            # Client connection has failed, reset connection status
            krpc_status = "no connection"
            self.is_connected = False
            self.is_data_streaming = False
            print("KRPC connection failure")
            print("Exception type    : ", type(e).__name__)
            print("Exception message : ", str(e))

        except Exception as e:
            print("Failed to get KRPC status")
            print("Exception type    : ", type(e).__name__)
            print("Exception message : ", str(e))

        return krpc_status

    def get_vessel_attitude(self) -> VesselAttitude:
        is_valid = False
        heading = 0
        pitch = 0
        roll = 0
        if self.is_connected and self.is_data_streaming:
            try:
                heading = self.stream_heading()
                pitch = self.stream_pitch()
                roll = self.stream_roll()
                is_valid = True
            except Exception as e:
                print("Failed to get KRPC vessel attitude")
                print("Exception type    : ", type(e).__name__)
                print("Exception message : ", str(e))
                self.is_data_streaming = False
        return VesselAttitude(is_valid, heading, pitch, roll)

    def get_vessel_flight_state(self) -> VesselFlightState:
        data = VesselFlightState(False, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        if self.is_connected and self.is_data_streaming:
            try:
                vessel = self.krpc_connection.space_center.active_vessel
                vessel_mass = self.stream_mass()
                vessel_cbody_refframe = self.stream_vessel_orbit().body.reference_frame
                vessel_pos = vessel.position(vessel_cbody_refframe)
                vessel_pos_vec = np.array([vessel_pos[0], vessel_pos[1], vessel_pos[2]])
                vessel_pos_mag2 = np.dot(vessel_pos_vec, vessel_pos_vec)
                vessel_pos_mag = math.sqrt(vessel_pos_mag2)
                vessel_pos_unit = vessel_pos_vec / vessel_pos_mag
                vessel_vel = vessel.velocity(vessel_cbody_refframe)
                vessel_vel_vec = np.array([vessel_vel[0], vessel_vel[1], vessel_vel[2]])
                vessel_vel_mag2 = np.dot(vessel_vel_vec, vessel_vel_vec)
                vessel_vel_mag = math.sqrt(vessel_vel_mag2)
                vessel_vel_unit = np.array([vessel_vel[0] / vessel_vel_mag, vessel_vel[1] / vessel_vel_mag, vessel_vel[2] / vessel_vel_mag])
                cbody_gravity = self.gravitational_constant * vessel.orbit.body.mass / vessel_pos_mag2

                vessel_srfvel_vec = project_vector_a_onto_plane_b(vessel_vel_vec, vessel_pos_unit)
                vessel_srfvel_mag2 = np.dot(vessel_srfvel_vec, vessel_srfvel_vec)
                vessel_srfvel_mag = math.sqrt(vessel_srfvel_mag2)
                vessel_srfvel_unit = vessel_srfvel_vec / vessel_srfvel_mag

                vessel_rot = vessel.rotation(vessel_cbody_refframe)
                vessel_rot_q = Quaternion(vessel_rot[3], vessel_rot[0], vessel_rot[1], vessel_rot[2])
                vessel_fwd = vessel_rot_q.rotate(np.array([0.0, 0.0, 1.0]))
                vessel_lat = vessel_rot_q.rotate(np.array([1.0, 0.0, 0.0]))

                surface_vessel_fwd = project_vector_a_onto_plane_b(vessel_fwd, vessel_pos_unit)
                surface_vessel_fwd = vector_normalize(surface_vessel_fwd)
                surface_vessel_lat = project_vector_a_onto_plane_b(vessel_lat, vessel_pos_unit)
                surface_vessel_lat = vector_normalize(surface_vessel_lat)

                surface_vessel_vel_fwd = project_a_onto_b(vessel_vel_vec, surface_vessel_fwd)
                surface_vessel_vel_lat = project_a_onto_b(vessel_vel_vec, surface_vessel_lat)

                vessel_ang_vel = vessel.angular_velocity(vessel_cbody_refframe)
                vessel_ang_vel_vec = np.array([vessel_ang_vel[0], vessel_ang_vel[1], vessel_ang_vel[2]])
                vessel_ang_vel_pitch = project_a_onto_b(vessel_ang_vel_vec, vessel_lat)
                vessel_ang_vel_yaw = project_a_onto_b(vessel_ang_vel_vec, vessel_fwd)

                self.draw_vessel_pos_unit.start = vessel_pos
                self.draw_vessel_pos_unit.end = vessel_pos_vec + (vessel_pos_unit * 10.0)
                self.draw_vessel_vel_unit.start = vessel_pos
                self.draw_vessel_vel_unit.end = vessel_pos + (vessel_vel_unit * 10.0)
                self.draw_vessel_srfvel_unit.start = vessel_pos
                self.draw_vessel_srfvel_unit.end = vessel_pos + (vessel_srfvel_unit * 10.0)
                self.draw_vessel_fwd_unit.start = vessel_pos
                self.draw_vessel_fwd_unit.end = vessel_pos + (surface_vessel_vel_lat * 10.0)

                data.iSituation = self.stream_situation()
                data.fWeight = cbody_gravity * vessel_mass
                data.fThrustMax = self.stream_max_thrust()
                data.fVerticalSpeed = vessel.flight(self.stream_vessel_orbit().body.reference_frame).vertical_speed
                data.fForwardSpeed = math.sqrt(np.dot(surface_vessel_vel_fwd, surface_vessel_vel_fwd)) * np.sign(np.dot(surface_vessel_vel_fwd, surface_vessel_fwd))
                data.fLateralSpeed = math.sqrt(np.dot(surface_vessel_vel_lat, surface_vessel_vel_lat)) * np.sign(np.dot(surface_vessel_vel_lat, surface_vessel_lat))
                data.fPitchSpeed = math.sqrt(np.dot(vessel_ang_vel_pitch, vessel_ang_vel_pitch)) * np.sign(np.dot(vessel_ang_vel_pitch, surface_vessel_lat))
                data.fPitchTorqueMax = self.stream_max_torque()[0][0]
                data.fPitchMomentOfInertia = self.stream_moi()[0]
                data.fYawSpeed = math.sqrt(np.dot(vessel_ang_vel_yaw, vessel_ang_vel_yaw)) * np.sign(np.dot(vessel_ang_vel_yaw, surface_vessel_fwd))
                data.fYawTorqueMax = self.stream_max_torque()[0][1]
                data.fYawMomentOfInertia = self.stream_moi()[1]
                data.bIsDataValid = True
            except Exception as e:
                print("Failed to get KRPC vessel flight state")
                print("Exception type    : ", type(e).__name__)
                print("Exception message : ", str(e))
                self.is_data_streaming = False
        return data

    def get_vessel_orbital_parameters(self) -> VesselOrbitalParameters:
        data = VesselOrbitalParameters(False, "", 0.0, 0.0, 0.0, 0.0)
        if self.is_connected and self.is_data_streaming:
            try:
                data.sCelestialBodyName = self.stream_vessel_orbit().body.name
                data.fCelestialBodyMass = self.stream_vessel_orbit().body.mass
                data.fPeriod = self.stream_vessel_orbit().period
                data.fTimeToApoapsis = self.stream_vessel_orbit().time_to_apoapsis
                data.fTimeToPeriapsis = self.stream_vessel_orbit().time_to_periapsis
                data.bIsDataValid = True
            except Exception as e:
                print("Failed to get KRPC vessel orbit")
                print("Exception type    : ", type(e).__name__)
                print("Exception message : ", str(e))
                self.is_data_streaming = False
        return data

    def get_vessel_resources(self) -> VesselResources:
        data = VesselResources(False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        if self.is_connected:
            try:
                (data.fWater, data.fWaterMax) = self.get_total_resource("Water")
                (data.fFood, data.fFoodMax) = self.get_total_resource("Food")
                (data.fOxygen, data.fOxygenMax) = self.get_total_resource("Oxygen")
                (data.fAtmo, data.fAtmoMax) = self.get_total_resource("Atmosphere")
                (data.fWasteAtmo, data.fWasteAtmoMax) = self.get_total_resource("WasteAtmosphere")
                data.bIsDataValid = True
            except Exception as e:
                print("Failed to get KRPC vessel resources")
                print("Exception type    : ", type(e).__name__)
                print("Exception message : ", str(e))
        return data

    def get_total_resource(self, resource_name: str) -> tuple:
        """ Returns the total amount of resource in the active vessel as a tuple: (amount, max)"""
        amount = 0
        max = 0
        all_resources = self.krpc_connection.space_center.active_vessel.resources.with_resource(resource_name)
        for r in all_resources:
            amount += r.amount
            max += r.max
        return (amount, max)

    def set_flight_controls(self, control: VesselFlightControl) -> None:
        if control.bIsInputValid:
            self.krpc_connection.space_center.active_vessel.control.throttle = control.fThrottle
            self.krpc_connection.space_center.active_vessel.control.pitch = control.fPitch
            self.krpc_connection.space_center.active_vessel.control.yaw = control.fYaw

    #
    # Private Methods
    #
    def __increase_retry_interval(self) -> None:
        self.retry_interval_ms = self.retry_interval_ms * 2
        if self.retry_interval_ms > self.MAX_RETRY_INTERVAL_MS:
            self.retry_interval_ms = self.MAX_RETRY_INTERVAL_MS

    def __execute_debugging_tools(self):
        parts_to_log = []
        vessel = self.krpc_connection.space_center.active_vessel
        root = vessel.parts.root
        stack = [(root, 0)]
        while stack:
            part, depth = stack.pop()
            print(' ' * depth, part.title)
            if 'ECLSS' in part.title:
                parts_to_log.append(part)
            elif 'Chemical' in part.title:
                parts_to_log.append(part)
            elif 'Geiger' in part.title:
                parts_to_log.append(part)
            elif 'Fuel Cell' in part.title:
                parts_to_log.append(part)
            for child in part.children:
                stack.append((child, depth+1))
        for part in parts_to_log:
            self.__print_part_info(part)

    def __print_part_info(self, krpc_part):
        print("\n\n\n\n=== {0} ===".format(krpc_part.title))
        for module in krpc_part.modules:
            info_str = "Module: {0}\n".format(module.name)

            idx = 0
            for field in module.fields_by_id:
                if idx == 0:
                    info_str += "Fields: "
                else:
                    info_str += "        "
                info_str += field + "  =  "
                info_str += module.fields_by_id[field] + "\n"

            num_events = len(module.events_by_id)
            for idx in range(0, num_events):
                # if ("ECLSS" in krpc_part.title) and ("Scrubber" in module.events[idx]):
                #     module.trigger_event_by_id(module.events_by_id[idx])
                #     print("\n\nTRIGGERED\n\n")
                if idx == 0:
                    info_str += "Events: "
                else:
                    info_str += "        "
                info_str += module.events[idx] + " (ID=" + module.events_by_id[idx] + ")\n"


            num_actions = len(module.actions_by_id)
            for idx in range(0, num_actions):
                if idx == 0:
                    info_str += "Action: "
                else:
                    info_str += "        "
                info_str += module.actions[idx] + " (ID=" + module.actions_by_id[idx] + ")\n"

            print(info_str)
