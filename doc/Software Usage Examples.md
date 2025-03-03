# Software Usage Examples

**Rpibeh** includes features such as video recording, real-time playback, rodent position tracking, motion pattern analysis, and the ability to output frame-by-frame video timestamps to synchronization with external devices, such as Open Ephys. This document provides examples of what the software can accomplish, showcasing its multifunctionality. Users are encouraged to explore further features based on their specific experimental paradigms. A full user guide is available [here](User Guide.md).



------

## 1. **Basic Video Recording without Closed-Loop Control**

This functionality allows for standard video recording. The software includes frame alignment functionality, enabling synchronization with external devices. Users can record videos while concurrently performing electrophysiological recordings, and later use the synchronized videos for data analysis. Post-recording analysis features include generating heatmaps of rodent movement, freezing state analysis, and specific area analysis.

For example, users can define regions of interest (ROIs) for analysis. After video recording, users can extract information such as the time the rodent spent in specific areas or the number of entries into defined regions, like a choice in a T-maze or different compartments in a three-chamber task.



------

## 2. **Area Detection and Feedback Control**

The software provides real-time rodent position detection, allowing for closed-loop control once the rodent enters a designated area (e.g., delivering a shock). Although the software currently supports tracking of a single rodent, in specific scenarios—such as multiple animals present but with sufficient space between them—users can select a region of interest within which to track a specific animal.

This functionality can be particularly useful in experiments where a certain region's activity triggers specific actions, enabling the implementation of tailored behavioral paradigms.



------

## 3. **Freezing State Detection with Closed-Loop Feedback**

Rpibeh can detect the "freezing" behavior in rodents in real-time. Upon detecting a freezing state, the software can output a closed-loop control signal, triggering external feedback devices such as optogenetic stimulation, sound, electrical stimulation, or visual cues. 



------

## 4. **User-Defined Methods**

RpiBeh allows users to define custom methods for real-time detection and closed-loop control. Users can write detection criteria based on raw frame images, rodent position, or specific keypoints and apply them to trigger feedback control mechanisms.

The user-defined methods provide high versatility and can be tailored to a wide range of experimental setups. For detailed instructions on how to create custom methods, refer to the [Custom Detection and Closed-Loop Control Documentation](Custom Detection and Closed-Loop Control.md).



------

This documentation provides just a few examples of the software’s multifunctionality, but the possibilities are vast. Users are encouraged to experiment with different setups to tailor the software for their specific research requirements. 

