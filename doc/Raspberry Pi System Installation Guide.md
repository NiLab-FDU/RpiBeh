# Raspberry Pi System Installation Guide

## 1. Download Raspberry Pi OS

1.1 Go to the official Raspberry Pi download page:

   [Raspberry Pi OS Download](https://downloads.raspberrypi.com/raspios_full_armhf/images/raspios_full_armhf-2022-09-26/2022-09-22-raspios-bullseye-armhf-full.img.xz)

   Download the image file to your local computer.



## 2. Flash the Raspberry Pi OS onto the SD Card

2.1 Prepare the following hardware:

- SD Card (minimum 8GB recommended)
- SD Card Reader
- Raspberry Pi device

2.2 Use the official software to install the OS onto the SD card. You can download the Raspberry Pi Imager from:

   [Raspberry Pi Imager Download](https://downloads.raspberrypi.org/imager/imager_latest.exe)

2.3 Flash the downloaded OS image onto the SD card:

- **Raspberry Pi Device**: Select `RASPBERRY PI 3` as the device model.
- **Operating System**: Select `Use custom` and browse to select the previously downloaded image.
- **Storage Device**: Choose the SD card. (Be careful to select the correct device to avoid data loss as the process will format the drive.)

2.4 Recommended configuration:

- Enable SSH
- Configure WiFi credentials (SSID and password)

2.5 After flashing is complete, safely eject the SD card and insert it into the Raspberry Pi.



## 3. Raspberry Pi System Configuration

There are two methods to configure the Raspberry Pi system:

### Method 1: Using a Display, Keyboard, and Mouse

This method requires you to connect the Raspberry Pi to a display, mouse, and keyboard.

- Power on the Raspberry Pi.
- Set up the system via the GUI (Graphical User Interface).

In `Interface Options`, enable the following:

- **Legacy Camera Enable**.
- **SSH Enable**.



### Method 2: Using SSH (Headless Setup)

This method does not require a display, mouse, or keyboard. You can access and configure the Raspberry Pi remotely over the network using SSH.

#### How to Find the Raspberry Pi IP Address

You can find the IP address of your Raspberry Pi by checking your router's device list or using network scanning tools like `nmap`.     **文档**

#### Connecting via SSH

You can use SSH clients such as:

- **PuTTY**: [Download PuTTY](https://www.putty.org/)
- **MobaXterm**: [Download MobaXterm](https://mobaxterm.mobatek.net/)

The default username is `pi`, and the default password is `raspberry`.



#### Initial Configuration

Run the configuration tool by entering:

```bash
sudo raspi-config
```


In `Interface Options`, enable the following:

- **Legacy Camera Enable** 
- **SSH Enable**



## 4. Transfer `rpi_server` Folder to the Raspberry Pi

You can transfer the `rpi_server` folder to the Raspberry Pi using one of the following methods:

### Method 1: Clone the Repository Using Git

1. SSH into the Raspberry Pi.
2. Run the following command to clone the repository:

```bash
git clone https://github.com/NiLab-FDU/RpiBeh.git
```

### Method 2: Transfer via SSH or FTP

- Use a file transfer protocol (FTP) or SSH to transfer the `rpi_server` folder from your computer to the Raspberry Pi.



## 5. Raspberry Pi 3B+ Assembly Details

### 5.1 Camera Assembly

1. Connect the camera module to the Raspberry Pi's camera port (located near the HDMI port).
2. Ensure the ribbon cable is inserted correctly, with the metal connectors facing the board.
3. Secure the camera module with screws or a case mount if necessary.

### 5.2 Fan Installation

1. Attach the fan to the Raspberry Pi using screws, mounting brackets, or the GPIO header pins, depending on your fan model.
2. If using GPIO pins for power, connect the fan to 5V and GND pins.

### 5.3 Heat Sink Setup

1. Place the heat sink directly onto the Raspberry Pi's CPU to help dissipate heat.
2. Gently press the heat sink onto the chip to ensure good contact and adhesion.

### 5.4 Wiring and GPIO Setup

- Connect external devices (e.g., sensors, relays) to the GPIO pins.
- Use the `GPIO.setmode(GPIO.BOARD)` method to define the pin numbering scheme.
- Ensure the wiring is correct and secure to prevent short circuits. Common GPIO pin connections include:
  - **Video frame alignment**: Use GPIO pin 11 for TTL output.
  - **Closed-loop control output**: Use GPIO pin 13 for output signaling.
  - **GND connection**: Ensure the ground is properly connected to the GND.
