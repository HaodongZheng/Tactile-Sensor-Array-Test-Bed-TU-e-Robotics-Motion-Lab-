import time
import struct
import inspect
from pymodbus.client import ModbusSerialClient
import numpy as np

PORT = "/dev/ttyUSB0"
SLAVE = 1
BAUDRATE = 57600

class LoadcellReader():
# Support different pymodbus versions
    def __init__(self,PORT="/dev/ttyUSB0",BAUDRATE=57600):
        self.client = ModbusSerialClient(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=0.02,
        )
        sig = inspect.signature(ModbusSerialClient.read_holding_registers)
        if "device_id" in sig.parameters:
            self.UNIT_KW = "device_id"
        elif "slave" in sig.parameters:
            self.UNIT_KW = "slave"
        elif "unit" in sig.parameters:
            self.UNIT_KW = "unit"
        else:
            raise RuntimeError(f"Unknown pymodbus API: {sig}")


    def reg_addr(self,reg_400xx: int) -> int:
        return reg_400xx - 40001


    def to_int16(self,x: int) -> int:
        return x - 65536 if x >= 32768 else x


    def regs_to_float_msw_lsw(self,reg_hi: int, reg_lo: int) -> float:
        raw = struct.pack(">HH", reg_hi, reg_lo)
        return struct.unpack(">f", raw)[0]


    def read_block(self):
        """
        Read 40063, 40064, 40065, 40066 in one transaction.

        40063: raw normalized net weight
        40064-40065: float technical net weight
        40066: status
        """
        rr = self.client.read_holding_registers(
            address=self.reg_addr(40063),
            count=4,
            **{self.UNIT_KW: SLAVE},
        )

        if rr.isError():
            raise RuntimeError(rr)

        r40063, r40064, r40065, r40066 = rr.registers

        raw_net = self.to_int16(r40063)
        float_net = self.regs_to_float_msw_lsw(r40064, r40065)
        status = r40066
        stable = bool(status & (1 << 4))

        return raw_net, float_net, status, stable


    def read_u16(self,reg_400xx: int) -> int:
        rr = self.client.read_holding_registers(
            address=self.reg_addr(reg_400xx),
            count=1,
            **{self.UNIT_KW: SLAVE},
        )
        if rr.isError():
            raise RuntimeError(rr)
        return rr.registers[0]


    def read_loadcell_value(self):
        try:
            raw_net, value, status, stable = self.read_block()
        except Exception as e:
            print("Read error:", e)
            return 0
        return value/2.0182/100
    
if __name__ == "__main__":
    ###### Example usage ######

    # If you are using windows, change the port accordingly to "COM"+"X", where X is the port number. 
    loadcell = LoadcellReader(PORT="/dev/ttyUSB0")
    force_value = loadcell.read_loadcell_value()
    print(f"Loadcell reading: {force_value} N")