from config import KRPC_IP_ADDRESS, KRPC_RPC_PORT, KRPC_STREAM_PORT, KBALL_MMAP_INTERFACE_FILE
from ksp_interface import KspInterface
from app import KmiffedApp
from mmap_interface import MemMapInterface

#
# KRPC Interface
#
krpc = KspInterface(
    ip_address=KRPC_IP_ADDRESS,
    rpc_port=KRPC_RPC_PORT,
    stream_port=KRPC_STREAM_PORT)

#
# Memory-Mapped Interface
#
mmap_filename = KBALL_MMAP_INTERFACE_FILE
mem_map = MemMapInterface(mmap_filename)
mem_map.init_mapping()


#
# Entry Point Routine
#
app = KmiffedApp(krpc, mem_map)
app.run()

krpc.deinit_connection()
mem_map.deinit_mapping()
