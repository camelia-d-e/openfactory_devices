"""
MTConnect Adapter for the WTVB01-485 vibration sensor from WitMotion

Uses RS485 Modbus RTU for communication
"""
import time

from .device_model import DeviceModel


class WTVB01:

    # default factory configuration
    baud_rate = 9600
    sensor_address = 0x50
    port = "COM7"

    DEBUG = False

    # sensor registers
    ACCX_REGISTER = 52
    VX_REGISTER = 58
    AX_REGISTER = 61
    TEMP_REGISTER = 64
    DX_REGISTER = 65
    HZX_REGISTER = 68

    __available__ = 1

    def __init__(self):
        self.sensor = DeviceModel("WTVB01-485", self.port, self.baud_rate, self.sensor_address)
        
        try:
            self.sensor.openDevice()
        except OSError as e:
            print(f"Error opening sensor device: {e}")

        self.connected = self.sensor.isOpen
        if self.connected:
            self.sensor.startLoopRead()
            time.sleep(0.5)
            print("Sensor connected")
        else:
            print(f"The device connected on {self.port} is not a WTVB01 sensor")

    def temperature(self):
        """
        Read temperature in degree Celcius
        """
        return self.sensor.get(str(self.TEMP_REGISTER))

    def displacements(self):
        """
        Read displacements in microns
        """
        disp_microns =  [self.sensor.get(str(self.DX_REGISTER)), self.sensor.get(str(self.DX_REGISTER+1)), self.sensor.get(str(self.DX_REGISTER+2))]
        return [(disp / 1000.0) if disp is not None else None for disp in disp_microns]  # Convert to mm

    def vibration_frequencies(self):
        """
        Read vibration frequencies in Hz
        """
        return [self.sensor.get(str(self.HZX_REGISTER)), self.sensor.get(str(self.HZX_REGISTER+1)), self.sensor.get(str(self.HZX_REGISTER+2))]

    def angles(self):
        """
        Read angles in degrees
        """
        return [self.sensor.get(str(self.AX_REGISTER)), self.sensor.get(str(self.AX_REGISTER+1)), self.sensor.get(str(self.AX_REGISTER+2))]
    
    def velocity(self):
        """ Read velocity in mm/s """
        return [self.sensor.get(str(self.VX_REGISTER)), self.sensor.get(str(self.VX_REGISTER+1)), self.sensor.get(str(self.VX_REGISTER+2))]
    
    def acceleration(self):
        """ Read acceleration in g """ 
        acc_g = [self.sensor.get(str(self.ACCX_REGISTER)), self.sensor.get(str(self.ACCX_REGISTER+1)), self.sensor.get(str(self.ACCX_REGISTER+2))]
        return [acc*9806.65 if acc is not None else None for acc in acc_g]  # Convert to mm/s^2

    def read_data(self):
        """
        Read and return device data
        """
        try:
            temp = self.temperature()
            disp = self.displacements()
            freq = self.vibration_frequencies()
            velocity = self.velocity()
            angles = self.angles()
        except OSError as e:
            print(f"Error reading data: {e}")
            return {}
            
        return {
            key: value
            for key, value in {
                "temp": temp,
                "dx": disp[0],
                "dy": disp[1],
                "dz": disp[2],
                "hx": freq[0],
                "hy": freq[1],
                "hz": freq[2],
                "vx": velocity[0],
                "vy": velocity[1],
                "vz": velocity[2],
                "angle_x": angles[0],
                "angle_y": angles[1],
                "angle_z": angles[2],
                "acc_x": self.acceleration()[0],
                "acc_y": self.acceleration()[1],
                "acc_z": self.acceleration()[2]
            }.items()
            if value is not None
        }