# IP Address Checking Methods for Raspberry Pi and Control Host

This document explains how to check the IP addresses of the control host and the Raspberry Pi. The control host is connected to the Raspberry Pi via an Ethernet cable or they are both on the same local area network (LAN). Both devices should be powered on during this process.



---

## Checking Control Host IP Address (Windows)

### Method 1: Using Command Prompt

1. Press **Win + R** to open the Run dialog.
2. Type `cmd` and press **Enter** to open the Command Prompt.
3. In the Command Prompt, type the following command:
   ```bash
   ipconfig

4. Look for the `IPv4 Address` under your active network adapter (e.g., Ethernet adapter or Wi-Fi adapter). This will display the local IP address of your Windows machine.

### Method 2: Using Network Settings

1. Click on the **Start Menu** and go to **Settings**.
2. Navigate to **Network & Internet**.
3. Click on **Status**, and then click on **Properties** for your active network connection.
4. Scroll down to find the **IPv4 Address**, which is your control host's IP address.



------

## Checking Raspberry Pi IP Address from the Control Host

### Method 1: Using Command Prompt

1. Open the **Command Prompt** on your Windows control host.

2. Type the following command to ping the Raspberry Pi (assuming the default hostname):

   ```
   ping raspberrypi.local
   ```

3. If successful, the Raspberry Pi's IP address will appear in the response.

> **Note**: If you encounter issues with `raspberrypi.local` not being recognized, ensure both devices are connected to the same network and that **Bonjour** or **mDNS** services are available.



------

## Checking Raspberry Pi IP Address Directly

### Method 1: Using `ifconfig`

1. Open the **Terminal** on the Raspberry Pi.

2. Type the following command to display network information:

   ```
   ifconfig
   ```

3. Look for the `inet` address under your active network interface (usually `eth0` for Ethernet or `wlan0` for Wi-Fi). This will be the IP address of the Raspberry Pi.



------

## Troubleshooting: Identifying the Correct IP Address

When using `ipconfig` on the control host or `ifconfig` on the Raspberry Pi, you may encounter multiple IP addresses, such as `127.0.0.1` (loopback address). To identify the correct local network IP address for communication:

1. **Look for the non-loopback address**: The address `127.0.0.1` is the local loopback address, which is not used for communication with other devices on the network. The correct local network IP address will be in the form of `192.x.x.x`, `10.x.x.x`, or `172.x.x.x`.
2. **Ensure both devices are on the same network**: If the addresses for both the control host and the Raspberry Pi are in the same range (e.g., `192.168.x.x`), they should be able to communicate over the local network.