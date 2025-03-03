# RpiBeh

RpiBeh is an open-source, cost-effective, and versatile software system designed for real-time neuroethological research in rodents. It integrates behavior tracking and closed-loop control in a modular and customizable framework suitable for various experimental setups.



## Features

* **Affordable and Customizable**: Built on Raspberry Pi, RpiBeh is an open-source, budget-friendly solution, offering extensive customization options for diverse experimental setups.

* **Real-Time Behavior Tracking**: Utilizes algorithms for real-time tracking and locomotion analysis:
  - **Background Subtraction Method (BSM)** for precise position tracking.

  - **Frame Difference (FD)** for detecting freezing behavior.

* **Behavior-Driven Closed-Loop Control**: Enables real-time video streaming and closed-loop intervention based on animal behavior, ideal for behavioral reinforcement experiments (e.g., place avoidance, social fear conditioning).

* **Precise Synchronization**: Provides frame-by-frame video timestamp output, ensuring accurate synchronization with external devices.



For more usage examples, please refer to [Software Usage Examples](doc/Software Usage Examples.md).



## Installation

RpiBeh consists of two main components:

- **Raspberry Pi Server** (`rpi_server`) – Installed on the Raspberry Pi for data capture and real-time control. Detailed installation steps can be found in the [Raspberry Pi System Installation Guide.md](doc/Raspberry Pi System Installation Guide.md).
- **Client Host** (`client_host`) – Installed on a control host for user interface (GUI) and data processing. Detailed installation steps can be found in the [Control Host Environment Setup Guide](doc/Control Host Environment Setup Guide.md).



**Prerequisites**

- Raspberry Pi 3B+
- Python 3.7 or higher for `Control host`; Python 2 for Raspberry Pi
- Dependencies: listed in `client_host\requirements.txt`



## Usage

Follow the steps below to run the software:

1. **On the Raspberry Pi**, execute the following command:

   ```python
   python rpi_server/scripts/rpi_host.py plugin
   ```

2. **On the Control Host**, execute the following command:

   ```python
   python client_host/GUI/MainGUI.py
   ```

3. **In the GUI**, configure the following port settings:

   - RPi port: `5555`
   - PC port: `12397`

Once this is set up, you can begin interacting with the software through the GUI. For detailed instructions on using the GUI, refer to the [User Guide](doc/User Guide.md).



### Advanced Usage

Additionally, **Rpibeh** supports the analysis of local videos. Instructions for local server usage can be found in the [Local Server Usage Instructions](doc/Local Server Usage Instructions.md).

**Rpibeh** provides a customizable framework for implementing real-time detection methods. Detailed instructions for setting up custom detection and closed-loop control are available in [Custom Detection and Closed-Loop Control](doc/Custom Detection and Closed-Loop Control.md).



## References

**DLC-Live**: The codebase is available at [DeepLabCut-live](https://github.com/DeepLabCut/DeepLabCut-live). This repository is associated with the following paper:
Kane, Gary; Lopes, Gonçalo; Sanders, Jonny; Mathis, Alexander; and Mathis, Mackenzie. *Real-time, low-latency closed-loop feedback using markerless posture tracking*, eLife, 2020. [Kane et al., eLife 2020](https://elifesciences.org/articles/61909).



**RPI Server Code**: The `rpi_server` part of the code is based on modifications of the code from the repository [RPiCameraPlugin](https://github.com/arnefmeyer/RPiCameraPlugin). The repository is associated with the following paper:

AF Meyer, J Poort, J O'Keefe, M Sahani, and JF Linden: _A head-mounted camera system integrates detailed behavioral monitoring with multichannel electrophysiology in freely moving mice_, Neuron, Volume 100, p46-60, 2018. [link (open access)](https://doi.org/10.1016/j.neuron.2018.09.020)



## Related Materials

- **DeepLabCut Model Export Documentation**: For detailed instructions on exporting a trained DeepLabCut model to a `.pb` file, refer to the [DeepLabCut Helper Functions Documentation](https://github.com/DeepLabCut/DeepLabCut/blob/main/docs/HelperFunctions.md#new-model-export-function).



## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).



## Contact 

If you have any questions, feel free to reach out: - Email: syq458766@gmail.com



### Citation
If you use this code in your research or project, please consider citing the following preprint:

Sun, Yiqi, Zhang, Jie, Wang, Qianyun, and Ni, Jianguang, "RpiBeh: a multi-purpose open-source solution for real-time tracking and behavior-driven closed-loop interventions in rodent neuroethology," bioRxiv, https://doi.org/10.1101/2024.12.02.626497, 2024.

