# User Guide for Real-Time Detection and Closed-Loop Control Software

This document provides detailed instructions for the usage, setup, and parameter settings of RpiBeh. The software is designed to operate on a Raspberry Pi and a host computer, enabling real-time detection and control of specific behavioral metrics, along with post-experiment analysis.

## Software Workflow Overview

### Step 1: Start Services

1. **On Raspberry Pi:**

   - Run the following Python script to start the Raspberry Pi service:

   ```bash
   python rpi_server/scripts/rpi_host.py plugin
   ```

2. **On Control Host:**

   - Run the following Python script to open the GUI page:

   ```bash
   python client_host/GUI/MainGUI.py
   ```

### Step 2: Connect and Configure

- **Fill in IP Address and Port:**
  - Enter the IP address and port number for the Raspberry Pi and the control host.
  - The default port for the Raspberry Pi is **5555**, and for the control host, it is **12397**.
- **Connect:**
  - Click the **'Connect'** button to establish a connection with the Raspberry Pi. If successful, the button will turn green. Clicking it again will disconnect.
- **Capture Background Image:**
  - Click the **'Capture'** button to capture the background image of the experimental setup.
- **Region of Interest (ROI) Setup:**
  - Click the **'Region of Interest Setting'** button to define the ROI and set the scale.
- **Select Detection Metrics:**
  - Choose the real-time detection metrics you wish to use. The available options are **Tracking**, **Freezing**, **Speed**, **Acceleration**, and **Position** (whether the animal enters a designated area). You can also select a custom detection method.
- **Select Closed-Loop Control:**
  - Choose the appropriate closed-loop control method for the selected detection metrics.
- **Select Analysis Options:**
  - Choose the desired post-experiment analysis metrics such as **Heat Map**, **Trajectory Map**, **Freezing Analysis**, and **Selected Area Analysis**.
- **Prepare for Recording:**
  - Click **Prepare** to ensure all configurations are correct and ready for recording.
- **Set File Saving Path:**
  - Enter the file path and name, then specify the duration of the recording.
- **Start Recording:**
  - Click the **'Start'** button to begin recording. The recording will stop automatically after the set time, or you can click **'Stop'** to end it manually.

------



## Detailed Parameter Settings

### 1. Main GUI Page

- **RpiCamera Section:**
  - Enter the IP address and port number for both the Raspberry Pi and the control host.
  - In the case of local video usage, set the Raspberry Pi address to `'127.0.0.1'`. Refer to the [Local Server Usage Instructions](Local Server Usage Instructions.md) for detailed guidelines.
  - For remote video detection, make sure both devices are on the same local network. Use the [IP Address Checking Methods](IP Address Checking Methods.md) to obtain the IP addresses.
  - Click **'Connect'** to establish the connection with the Raspberry Pi.
- **Realtime Detection Section:**
  - Choose the real-time detection metrics you want:
    - **Tracking** (for movement tracking)
    - **Freezing** (for identifying freezing events)
    - **Speed** (for velocity detection)
    - **Acceleration** (for acceleration monitoring)
    - **Position** (for detecting if the animal enters a specific area)
  - Custom detection methods can also be added by selecting the **Custom** option.
  - Some options (e.g., Freezing, Speed, Acceleration, Position) require **Tracking** to be enabled.
- **Close Loop Section:**
  - The closed-loop control options are shown here, but only appear once corresponding detection metrics are selected in the Realtime Detection section.
  - Click the **'Setting'** button to adjust closed-loop control parameters (see the **Setting** section for detailed instructions).
- **Analysis Section:**
  - Choose the analysis methods you want:
    - **Heat Map** (for tracking animal's region occupancy)
    - **Trajectory Map** (for visualizing movement paths)
    - **Freezing Analysis** (to identify fear response thresholds)
    - **Selected Area Analysis** (for detailed analysis of specified areas, e.g., entry frequency, duration, total stay time, etc.)
- **Record Section:**
  - Set the directory for saving the recorded data by entering the path or using the **'Browse'** button.
  - Set the trial name, which will be appended with the timestamp of the recording.
  - Set the desired recording duration.
  - Click **'Prepare'** to check the configuration before starting. If DLC-live tracking is selected, wait for model initialization.
  - Click **'Start'** to begin the recording, and click **'Stop'** to end it manually.

------



### 2. GUI Menu Bar

- **File Menu:**
  - **'Save Config'**: Save the current configuration to a file.
  - **'Load Config'**: Load a previously saved configuration.
  - Configurations are automatically saved and loaded at the start and end of the software session in the `client_host/GUI/last_config.json` file.
- **Setting Menu:**
  - Access various configuration pages to adjust specific settings for the software.

------



### 3. Setting Pages

- **Camera Settings Page:**
  - Set video recording parameters, including frame rate and image size.
- **Region of Interest Settings Page:**
  - Define the area of interest (ROI) for tracking, freezing, and custom methods.
  - ROI shapes: **Rectangle**, **Circle**, **Polygon**.
    - **Rectangle:** Click and drag the mouse to select a rectangular area.
    - **Circle:** Click and drag the mouse to define a circular area, with the starting point as the center.
    - **Polygon:** Click to define multiple vertices that form a polygon.
  - Click the corresponding shape button, then select the region on the left. Use **'Set Scale'** to calibrate the scale based on a known real-world distance.
- **Tracking Settings Page:**
  - Select the tracking method. Options include:
  - **Background Subtraction**
  - **DLC-live** (DeepLabCut tracking)
  - If you select the **DLC-live** method, you'll need to specify the path to the folder containing the exported DeepLabCut model. This folder should include the trained model files necessary for animal tracking.
    - **Path:** Browse and select the folder path that contains the exported DLC model (e.g., `xx/exported-models/DLC_Propulsion_resnet_50_iteration-0_shuffle-1`).
    - **Loading the Model:** After selecting the path, click the **'Load'** button to load the model. Once loaded, the names of the keypoints used for tracking will appear.
    - After the model is loaded, you can choose which keypoints (e.g., animal's head, tail, or paws) to track. The software will use the average position of the selected keypoints to estimate the animal’s overall position.
- **Detection Settings Page:**
  - Adjust detection parameters for **Freezing**, **Speed**, and **Acceleration**.
  - Set thresholds for each detection, including directionality and duration.
  - Speed and Acceleration detection allow for directionality adjustment (over or below threshold), as well as smoothing parameters. The XY smoothing refers to smoothing the XY coordinates used for speed/acceleration calculations, while the "Smooth" option applies to the speed/acceleration values themselves. Median filtering is used for smoothing, with the window size (in frames) selectable. A value of 0 indicates no smoothing applied.
- **Position Settings Page:**
  - Set up area detection for tracking when the animal enters a specified region (e.g., Rectangle, Circle, or Polygon).
- **Close Loop Settings Page:**
  - This page allows you to set up parameters for the closed-loop control, which provides feedback to the animal based on real-time detection.
    - **Duration of each signal:**
      - Define the duration for which the stimulus (e.g., electrical stimulation or light pulse) will be applied once an event is detected.
      - **0** means the stimulus will be applied immediately when the event is detected and will continue until the event is no longer true.
    - **Signal delay after time:**
      - Set the delay in seconds between the event detection and the initiation of the stimulus.
    - **Signal Interval:**
      - Define the time between consecutive stimuli if the event continues over multiple periods.
      - **0** will trigger only a single stimulus per event detection.
      - **>0** will apply continuous stimulation with a set interval between stimuli.
- **Selected Area Analysis Settings Page:**
  - Configure the analysis for multiple regions, allowing overlapping areas for more flexible analysis.
  - User can clear the most recent selection using the **'Clear Last'** button or start a new selection by clicking the shape button again.

