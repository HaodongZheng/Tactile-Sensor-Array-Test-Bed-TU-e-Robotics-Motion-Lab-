# Tactile Sensor Array Test Bed (TU/e Robotics Motion Lab)
This is the repository for holding the codes, 3D printing files and instructions for the tactile sensor test bed at TU/e Robotics &amp; Motion Lab.

## Setting up environment
The setup guide is mainly tested Ubuntu 20.04, subtle differences might exist for different OS and versions.

## Safty measures
Although the CNC machine comes with a stop switch, depending on the indenter head and the sensor setup of your choice, the stop switch might not protect the indentation head from hitting the wooden bed or your sensors, which could cause damage to both the setup and the sensors. 

## Controlling CNC via G code
The movement of the indentation head is controlled by sending G code to the CNC machine. If you want to learn about G code, checkout this. Example codes are provided in this repository.

## Loadcell readout through serial port via ModBus protocol
The loadcell readings goes through Z-SG amplifier module (check mannual), at current stage, max readout frequency is at 100Hz. It is also possible to read the amplified analog signal, the current setup is designed to perform readout through the serial port.

## Making you own easy-swap indentation head for testing
In this repository I provide a template for making your own indentation head, which can be easily mounted on the setup without the need of extra tools.
