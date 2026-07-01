# Tactile Sensor Array Test Bed (TU/e Robotics Motion Lab)
This is the repository for holding the codes, 3D printing files and instructions for the tactile sensor test bed at TU/e Robotics &amp; Motion Lab.
## Setting up environment

The setup guide is mainly tested on Ubuntu 20.04. Subtle differences might exist for different operating systems and versions.

Clone this repository and enter the repository folder:

```bash
git clone https://github.com/HaodongZheng/Tactile-Sensor-Array-Test-Bed-TU-e-Robotics-Motion-Lab.git
cd Tactile-Sensor-Array-Test-Bed-TU-e-Robotics-Motion-Lab
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate the virtual environment with:

```bash
.venv\Scripts\activate
```

Install the required Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install numpy pymodbus pyserial
```

The dependency `pymodbus` is used for reading the Z-SG loadcell amplifier through the ModBus protocol. The dependency `pyserial` is used for communicating with the CNC controller through the serial port. `numpy` is used by the loadcell readout script.

On Linux, the serial device usually appears as `/dev/ttyUSB0`. If you get a permission error when opening the serial port, add your user to the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```

After running this command, log out and log back in for the permission change to take effect.

You can then test the CNC controller script with:

```bash
python scripts/NewIndenter.py
```

and test the loadcell readout script with:

```bash
python scripts/LoadcellReader.py
```

On Windows, change the serial port in the scripts to the correct COM port, for example:

```python
PORT = "COM3"
```

for the loadcell reader, or:

```python
INDENTER_PORT = "COM9"
```

for the CNC controller.

## Safty measures
Although the CNC machine comes with a stop switch, depending on the indenter head and the sensor setup of your choice, the stop switch might not protect the indentation head from hitting the wooden bed or your sensors, which could cause damage to both the setup and the sensors. 

## Controlling CNC via G code
The movement of the indentation head is controlled by sending G code to the CNC machine. If you want to learn about G code, checkout this. A ready-to-use class "NewIndenter" is provided with example usages in scripts/NewIndenter.py to make the process easy.

## Loadcell readout through serial port via ModBus protocol
The loadcell readings goes through Z-SG amplifier module (check mannual), at current stage, max readout frequency is at 100Hz. It is also possible to read the amplified analog signal, the current setup is designed to perform readout through the serial port. A ready-to-use class "LoadcellReader" is provided with example usages in scripts/LoadcellReader.py. 


## Making your own easy-swap indentation head for testing
In this repository I provide a template for making your own indentation head, which can be easily mounted on the setup without the need of extra tools.
