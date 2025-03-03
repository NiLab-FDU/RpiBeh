# Custom Detection and Closed-Loop Control

The **Custom.py** file provides a customizable framework for implementing real-time detection methods. By modifying the functions within this file, users can develop tailored detection criteria to suit various experimental needs.



## Customization Overview

To begin customizing the detection method, simply modify the functions within **Custom.py**. Below is an overview of the customizable elements:

### Custom Variables:

```python
Custom_name = 'CustomName'

# 'frame', 'xy', 'dlc-live key points'
input_data_type = 'dlc-live key points'
```

- **Custom_name**: This variable allows you to specify the name of the custom function for easier identification.

- input_data_type

  : Specifies the input type for the detection function. It can take one of three values:

  - `'frame'`: Input is an image frame, represented as (frame_size, frame_size, 3).
  - `'xy'`: Input is the tracked position (x, y) of the rodent's center.
  - `'dlc-live key points'`: Input is the set of key points detected by `dlc-live` for the rodent, with the shape of `(n, 3)`, where `n` is the number of key points, and each point consists of `x`, `y`, and `likelihood`.

### Functions to Modify

Based on the selected input type, you can modify one of the following functions to implement your custom detection:

- **get_res_frame(frame, timestamp, scale)**: Used when the input is an image frame.
- **get_res_xy(x, y, timestamp, scale)**: Used when the input is the rodent's center coordinates.
- **get_res_dlc(point_list, timestamp, scale)**: Used when the input is key points detected by `dlc-live`.

Each function provides the following parameters:

- `frame`: The image frame data (only for `'frame'` input type).
- `x, y`: The coordinates (only for `'xy'` input type).
- `point_list`: A list of key points (only for `'dlc-live key points'` input type).
- `timestamp`: The timestamp for the current frame.
- `scale`: The scale for distance calculation, typically in cm/pixel.
- `area_type`: The type of the area of interest for detection. It can be one of the following:
  - `'rectangle'`: Specifies a rectangular region.
  - `'oval'`: Specifies an elliptical (oval) region.
  - `'polygon'`: Specifies a polygonal region.
- `area_points`: The points that define the area of interest. 

These functions should return either `True` or `False` based on your detection criteria:





## Customization Examples

### Example 1: LED Light Detection

This example detects whether an LED light is on by checking the maximum pixel value of the frame.

```python
import numpy as np

Custom_name = 'LED'

# 'frame', 'xy', 'dlc-live key points'
input_data_type = 'frame'

def get_res_frame(frame, timestamp, scale, area_type, area_points):
    res = np.max(frame) > 200  # Checks if any pixel exceeds a brightness threshold
    return res

def get_res_xy(x, y, timestamp, scale, area_type, area_points):
    return False

def get_res_dlc(point_list, timestamp, scale, area_type, area_points):
    return False
```

In this example, the function `get_res_frame` checks the pixel intensity of the frame to detect the presence of light.  If any pixel exceeds a brightness threshold, it returns `True`, triggering the event.

### Example 2: Mouse Facing Right Detection

This example uses `dlc-live` key points to determine the orientation of the mouse, specifically whether the mouse is facing to the right.

```python
Custom_name = 'Clockwise'

# 'frame', 'xy', 'dlc-live key points'
input_data_type = 'dlc-live key points'

def get_res_frame(frame, timestamp, scale, area_type, area_points):
    return False

def get_res_xy(x, y, timestamp, scale, area_type, area_points):
    return False

import math
import numpy as np
last_res = False

def get_res_dlc(point_list, timestamp, scale, area_type, area_points):
    # Here, the order of key points is neck, back, tailbase
    global last_res
    if np.isnan(point_list).any():
        return last_res
    N = point_list[0]
    B = point_list[1]
    T = point_list[2]
    BT = (T[0] - B[0], T[1] - B[1])
    BN = (N[0] - B[0], N[1] - B[1])
    cross = BT[0] * BN[1] - BT[1] * BN[0]
    # dot = BT[0] * BN[0] + BT[1] * BN[1]
    # mag_BT = math.sqrt(BT[0] ** 2 + BT[1] ** 2)
    # mag_BN = math.sqrt(BN[0] ** 2 + BN[1] ** 2)
    # cos_theta = dot / (mag_BT * mag_BN)
    # theta = np.degrees(np.arccos(cos_theta))
    res = cross < 0
    last_res = res
```

This function determines whether a mouse is turning clockwise during locomotion by analyzing the relative positions of key points: neck, back, and tailbase. It calculates a straight line from the back center to the tailbase and assesses whether the neck point lies to the right (clockwise) or left (anticlockwise) of this line using a cross-product method. By default, the function returns `True` if the turning is clockwise, determined by `res = cross > 0`. To detect anticlockwise turning instead, modify the condition to `res = cross < 0`. Additionally, the function computes the angle between the neck, back, and tailbase, allowing users to impose further constraints based on this angle. A demonstration of the effect is provided below.

<img src="assets/clockwise_detection_example.gif" width="25%">



## Conclusion

By modifying these functions, users can easily implement customized real-time detection criteria for a variety of experimental setups. The ability to choose between frame analysis, coordinate tracking, or key point-based detection provides the flexibility to tailor the system to meet specific research needs.