# Tactile Sensor Array Test Bed (TU/e Robotics & Motion Lab)

This repository contains code, 3D-printing files, and setup instructions for the tactile sensor array test bed at the TU/e Robotics & Motion Lab.

The test bed is designed for controlled indentation experiments with tactile sensor arrays. It includes example scripts for controlling the CNC-based indenter and reading force measurements from a loadcell through a Z-SG amplifier module.

## Repository structure

```text
.
├── 3D_printed_parts/
│   ├── README.md
│   ├── swap_indenter_head_template.step
│   └── swap_indenter_head_template.stl
│
├── scripts/
│   ├── README.md
│   ├── LoadcellReader.py
│   └── NewIndenter.py
│
├── LICENSE
└── README.md
```

The `scripts/` folder contains the Python scripts for controlling the CNC-based indenter and reading the loadcell signal. The `3D_printed_parts/` folder contains the template files for making an easy-swap indentation head.


## Setting up the environment

The setup guide has mainly been tested on Ubuntu 20.04. Small differences may exist for other operating systems or versions.

Clone this repository and enter the repository folder:

```bash
git clone https://github.com/HaodongZheng/Tactile-Sensor-Array-Test-Bed-TU-e-Robotics-Motion-Lab.git
cd Tactile-Sensor-Array-Test-Bed-TU-e-Robotics-Motion-Lab
```

It is recommended to use a Python virtual environment to avoid conflicts with other Python packages. Here, the environment is named `tactile-testbed-env`:

```bash
python3 -m venv tactile-testbed-env
source tactile-testbed-env/bin/activate
```

On Ubuntu/Debian, if the `venv` module is not available, install it with:

```bash
sudo apt update
sudo apt install python3-venv
```

On Windows Command Prompt, activate the virtual environment with:

```bat
tactile-testbed-env\Scripts\activate.bat
```

On Windows PowerShell, use:

```powershell
.\tactile-testbed-env\Scripts\Activate.ps1
```

Install the required Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install numpy pymodbus pyserial
```

If you do not want to use a virtual environment, you can also install the dependencies directly into your current Python environment:

```bash
python3 -m pip install numpy pymodbus pyserial
```

## Serial port permissions on Linux

On Linux, the CNC controller or loadcell amplifier usually appears as a serial device such as `/dev/ttyUSB0`.

If you get a permission error when opening the serial port, add your user to the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```

After running this command, log out and log back in for the permission change to take effect.

## Safety concerns

Although the CNC machine has a stop switch, the stop switch may not fully protect the indentation head, the tactile sensor, or the wooden bed in all configurations.

Depending on the mounted indentation head and sensor setup, an incorrect command may cause the indentation head to collide with the sensor or the bed. Before running any motion command, carefully check:

* the current position of the indentation head;
* the coordinate frame and origin setting;
* the target `X`, `Y`, and `Z` positions;
* the feedrate;
* the available clearance above the sensor.

Always start with slow and small motions when testing a new setup.

## Controlling the CNC machine with G-code

The movement of the indentation head is controlled by sending G-code commands to the CNC machine.

A ready-to-use Python class, `NewIndenter`, is provided in:

```text
scripts/NewIndenter.py
```

The script initializes the serial connection, sets the controller to millimeter units with `G21`, enables absolute positioning with `G90`, and provides a simple `move_to(...)` function for commanding the indentation head.

You can test the CNC controller script with:

```bash
python scripts/NewIndenter.py
```

Before running an experiment, set the current position as the origin only after you have carefully checked the physical setup:

```python
indenter.set_current_position_as_origin()
```

Then the indentation head can be moved with:

```python
x_pos, y_pos, z_pos = your_desired_x, your_desired_y, your_desired_z
indenter.move_to(x=x_pos, y=x_pos, z=x_pos, feedrate=1000)
```

The unit of length is millimeters.

On Windows, change the serial port in the script to the correct COM port, for example:

```python
INDENTER_PORT = "COM9"
```

On Linux, the port is usually something like:

```python
INDENTER_PORT = "/dev/ttyUSB0"
```

## Loadcell readout through Modbus RTU

The loadcell signal is read through a Z-SG amplifier module using Modbus RTU over a serial connection.

A ready-to-use Python class, `LoadcellReader`, is provided in:

```text
scripts/LoadcellReader.py
```

The script reads the loadcell value through the serial port and returns the force reading in newtons.

You can test the loadcell readout script with:

```bash
python scripts/LoadcellReader.py
```

On Linux, the default serial port is:

```python
PORT = "/dev/ttyUSB0"
```

On Windows, change the port to the correct COM port, for example:

```python
PORT = "COM3"
```

The default baudrate in the script is:

```python
BAUDRATE = 57600
```
 
Make sure that the serial port, baudrate, and Modbus slave address match the configuration of the Z-SG amplifier module if you change its settings (Do not recommend).

## Making your own easy-swap indentation head

This repository provides a template for making custom indentation heads that can be mounted on the test bed without additional tools.

The 3D-printable parts are provided in:

```text
3D_printed_parts/
```

When designing a new indentation head, make sure that it does not collide with the tactile sensor, the mounting structure, or the wooden bed during motion.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
