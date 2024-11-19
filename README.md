# RpiBeh

RpiBeh, an open-source, cost-effective, and versatile software tailored for rodent neuroethological research.



## Installation

`rpi_server`runs on a **Raspberry Pi**

`client_host`runs on a **Control Host**



Install dependencies:

```bash
pip install -r requirements.txt
```



## Usage

1. In Raspberry Pi, run:

   ``` bash
   python rpi_server/scripts/rpi_host.py plugin
   ```

2. In Control Host, run:

   ``` bash
   python client_host/GUI/MainGUI.py
   ```
   



In GUI, Rpi port set: 5555, PC port set: 12397





## References

**DLC-Live**: The codebase is available at [DeepLabCut-live](https://github.com/DeepLabCut/DeepLabCut-live). This repository is associated with the following paper:
Kane, Gary; Lopes, Gonçalo; Sanders, Jonny; Mathis, Alexander; and Mathis, Mackenzie. *Real-time, low-latency closed-loop feedback using markerless posture tracking*, eLife, 2020. [Kane et al., eLife 2020](https://elifesciences.org/articles/61909).



**RPI Server Code**: The `rpi_server` part of the code is based on modifications of the code from the repository [RPiCameraPlugin](https://github.com/arnefmeyer/RPiCameraPlugin). The repository is associated with the following paper:

AF Meyer, J Poort, J O'Keefe, M Sahani, and JF Linden: _A head-mounted camera system integrates detailed behavioral monitoring with multichannel electrophysiology in freely moving mice_, Neuron, Volume 100, p46-60, 2018. [link (open access)](https://doi.org/10.1016/j.neuron.2018.09.020)



## Related Materials

- **DeepLabCut Model Export Documentation**: For detailed instructions on exporting a trained DeepLabCut model to a `.pb` file, refer to the [DeepLabCut Helper Functions Documentation](https://github.com/DeepLabCut/DeepLabCut/blob/main/docs/HelperFunctions.md#new-model-export-function).



## Contact 

If you have any questions, feel free to reach out: - Email: syq458766@gmail.com

