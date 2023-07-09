from ksp_interface import VesselAttitude
import mmap, os, struct

class MemMapInterface:
    #
    # Constants
    #
    __VESSEL_ATTITUDE_STRUCT_FMT = "<IIfff" # '<' denotes little-endian byte order
    __VESSEL_ATTITUDE_STRUCT_SIZE = struct.calcsize(__VESSEL_ATTITUDE_STRUCT_FMT)
    __VESSEL_ATTITUDE_STRUCT_MAGIC = 0x00CD0186

    #
    # Constructor
    #
    def __init__(self, mmap_filename):
        self.mmap_filename = mmap_filename
        self.vessel_attitude_struct = {
            'uMagic': self.__VESSEL_ATTITUDE_STRUCT_MAGIC,
            'uNonce': 0,
            'fHeading': 0,
            'fPitch': 0,
            'fRoll': 0,
        }

    #
    # Public Methods
    #
    def init_mapping(self):
        # Check if the file exists
        if os.path.exists(self.mmap_filename):
            # Open the file in read and write binary mode
            with open(self.mmap_filename, "r+b") as init_fd:
                # Write data at offset zero
                init_fd.seek(0)
                init_fd.write(struct.pack(
                    self.__VESSEL_ATTITUDE_STRUCT_FMT,
                    self.vessel_attitude_struct['uMagic'],
                    self.vessel_attitude_struct['uNonce'],
                    self.vessel_attitude_struct['fHeading'],
                    self.vessel_attitude_struct['fPitch'],
                    self.vessel_attitude_struct['fRoll']))
        else:
            # Create the file and open it in write binary mode
            with open(self.mmap_filename, "wb") as init_fd:
                # Write data at offset zero
                init_fd.write(struct.pack(
                    self.__VESSEL_ATTITUDE_STRUCT_FMT,
                    self.vessel_attitude_struct['uMagic'],
                    self.vessel_attitude_struct['uNonce'],
                    self.vessel_attitude_struct['fHeading'],
                    self.vessel_attitude_struct['fPitch'],
                    self.vessel_attitude_struct['fRoll']))

        # Map the file into memory
        self.mmap_file = open(self.mmap_filename, 'r+b')
        self.mapped_memory = mmap.mmap(self.mmap_file.fileno(), self.__VESSEL_ATTITUDE_STRUCT_SIZE)

    def deinit_mapping(self):
        self.mapped_memory.close()

    def set_vessel_attitude(self, attitude: VesselAttitude) -> None:
        if not attitude.bIsDataValid:
            return

        self.vessel_attitude_struct['uNonce'] += 1
        self.vessel_attitude_struct['fHeading'] = attitude.fHeading
        self.vessel_attitude_struct['fPitch'] = attitude.fPitch
        self.vessel_attitude_struct['fRoll'] = attitude.fRoll
        self.mapped_memory[0:self.__VESSEL_ATTITUDE_STRUCT_SIZE] = \
            struct.pack(self.__VESSEL_ATTITUDE_STRUCT_FMT,
                self.vessel_attitude_struct['uMagic'],
                self.vessel_attitude_struct['uNonce'],
                self.vessel_attitude_struct['fHeading'],
                self.vessel_attitude_struct['fPitch'],
                self.vessel_attitude_struct['fRoll'])
