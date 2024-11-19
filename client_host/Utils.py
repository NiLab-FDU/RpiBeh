import cv2
import numpy as np


def Log_thread_begin(thread_name):
    print(f'Thread Begin: {thread_name} ----------------------------')


def Log_thread_finish(thread_name):
    print(f'Thread Finish: {thread_name} ----------------------------')


def get_edge_and_center(thresh, use_open_close=True):
    if use_open_close:
        kernel = np.ones((5, 5), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None, np.nan, np.nan

    largest_contour = max(contours, key=cv2.contourArea)
    # epsilon = 0.01 * cv2.arcLength(largest_contour, True)
    # largest_contour = cv2.approxPolyDP(largest_contour, epsilon, True)

    M = cv2.moments(largest_contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = np.nan, np.nan  # Handle the case of division by zero
        print("not find")

    return largest_contour, cX, cY


def get_largest_component_and_center(frame, background, thresh_type='auto', thresh=100, diff_type='div', div_coeff=0.1,
                                     thresh_img_type='color_and', use_open_close=True, get_edge=True,
                                     area_type=None, area_points=None):
    """

    :param frame:
    :param background:
    :param thresh_type: 'manual', 'auto'. default: 'auto'
    :param thresh: use when thresh_type is 'manual': 0-255. default: 100
    :param diff_type: 'sub', 'div'. default: 'div'
    :param div_coeff: use when diff_type is 'div': >=0. default: 0.1
    :param thresh_img_type: 'gray', 'color_merge', 'color_and'. default: 'color_and'
    :param use_open_close: True/False. default: True
    :return:
    """

    def do_thresh(img_diff, thresh, thresh_type):
        # if thresh_type == 'adapt':
        #     return None, cv2.adaptiveThreshold(img_diff, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        #                                        cv2.THRESH_BINARY, 11, 2)
        if thresh_type == 'manual':
            return cv2.threshold(img_diff, thresh, 255, cv2.THRESH_BINARY)
        else:
            # thresh_type == 'auto'
            return cv2.threshold(img_diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if diff_type == 'sub':
        difference = cv2.absdiff(frame, background)
    else:
        # diff_type == 'div':
        coefficient = div_coeff
        modified_background = background.astype(np.float32) + coefficient
        difference = np.clip((cv2.absdiff(frame, background).astype(np.float32)) * 255 / modified_background, 0, 255)
        difference = difference.astype(np.uint8)

    if area_type is not None:
        difference = apply_mask(difference, area_type, area_points)

    if thresh_img_type == 'gray':
        gray_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
        thresh_value, thresh_img = do_thresh(gray_diff, thresh, thresh_type)
    else:
        B, G, R = cv2.split(difference)
        thresh_value_B, thresh_img_B = do_thresh(B, thresh, thresh_type)
        thresh_value_G, thresh_img_G = do_thresh(G, thresh, thresh_type)
        thresh_value_R, thresh_img_R = do_thresh(R, thresh, thresh_type)
        if thresh_img_type == 'color_merge':
            thresh_img = cv2.merge([thresh_img_B, thresh_img_G, thresh_img_R])
        else:
            # thresh_img_type == 'color_and'
            thresh_img = np.logical_and(thresh_img_B,
                                        np.logical_and(thresh_img_G, thresh_img_R)).astype(np.uint8) * 255

    if not get_edge:
        return difference, thresh_img, None, None, None

    largest_contour, cX, cY = get_edge_and_center(thresh_img, use_open_close)

    # thresh_img = cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)
    return difference, thresh_img, largest_contour, cX, cY


def point_in_area(area_type, area_points, x, y):
    if area_type == 'rectangle':
        x1, y1, x2, y2 = area_points
        return x1 <= x <= x2 and y1 <= y <= y2
    elif area_type == 'oval':
        x1, y1, x2, y2 = area_points
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius_x = (x2 - x1) / 2
        radius_y = (y2 - y1) / 2
        return ((x - center_x) ** 2) / (radius_x ** 2) + ((y - center_y) ** 2) / (radius_y ** 2) <= 1
    elif area_type == 'polygon':
        return cv2.pointPolygonTest(np.array(area_points, dtype=np.float32).reshape((-1, 1, 2)), (x, y), False) >= 0


def point_in_exclude_area(area_types, area_points, x, y):
    return point_in_area(area_types[0], area_points[0], x, y) and \
           (not point_in_area(area_types[1], area_points[1], x, y))


def convert_ndarray(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def cv2_fill(mask, area_type, area_points, color):
    if area_type == 'rectangle':
        cv2.rectangle(mask, (int(area_points[0]), int(area_points[1])),
                      (int(area_points[2]), int(area_points[3])), color, -1)
    elif area_type == 'oval':
        center = (int((area_points[0] + area_points[2]) // 2),
                  int((area_points[1] + area_points[3]) // 2))
        axes = (int((area_points[2] - area_points[0]) // 2),
                int((area_points[3] - area_points[1]) // 2))
        cv2.ellipse(mask, center, axes, 0, 0, 360, color, -1)
    elif area_type == 'polygon':
        pts = np.array(area_points, dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(mask, [pts], color)
    return mask


def apply_mask(image, area_type, area_points):
    mask = np.ones(image.shape, dtype=np.uint8) * 255
    mask = cv2_fill(mask, area_type, area_points, (0, 0, 0))

    masked_image = cv2.bitwise_and(image, cv2.bitwise_not(mask))
    return masked_image
