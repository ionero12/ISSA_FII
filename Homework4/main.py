import cv2
import numpy as np

cam = cv2.VideoCapture('C:/Users/Ione/Downloads/Lane_Detection_Test_Video_01.mp4')

left_top_point = (0, 0)
left_bottom_point = (0, 0)
right_top_point = (0, 0)
right_bottom_point = (0, 0)

while True:
    ret, frame = cam.read()
    if ret is False:
        break

    # ex2
    original_height, original_width, _ = frame.shape
    new_width = 350
    new_height = 250
    resized_frame = cv2.resize(frame, (new_width, new_height))
    cv2.imshow('Resized', resized_frame)

    # ex3
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Grayscale', gray_frame)

    # ex4
    trapezoid_frame = np.zeros_like(gray_frame)
    pt_upper_right = (int(new_width * 0.55), int(new_height * 0.75))
    pt_upper_left = (int(new_width * 0.45), int(new_height * 0.75))
    pt_bottom_left = (int(new_width * 0.1), new_height)
    pt_bottom_right = (int(new_width * 0.9), new_height)
    pts = np.array([pt_upper_right, pt_upper_left, pt_bottom_left, pt_bottom_right], dtype=np.int32)
    cv2.fillConvexPoly(trapezoid_frame, pts, 1)
    road_frame = gray_frame * trapezoid_frame
    cv2.imshow('Road', road_frame)

    # ex5
    upper_right = (new_width, 0)
    upper_left = (0, 0)
    bottom_left = (0, new_height)
    bottom_right = (new_width, new_height)
    trapezoid_bounds = np.array([upper_right, upper_left, bottom_left, bottom_right])
    trapezoid_bounds = np.float32(trapezoid_bounds)
    pts = np.float32(pts)
    magic_matrix = cv2.getPerspectiveTransform(pts, trapezoid_bounds)
    top_down_frame = cv2.warpPerspective(road_frame, magic_matrix, (new_width, new_height))
    cv2.imshow('Top-down', top_down_frame)

    # ex6
    blured_frame = cv2.blur(top_down_frame, ksize=(5, 5))
    cv2.imshow('Blur', blured_frame)

    # ex7
    copy1 = blured_frame.copy()
    copy2 = blured_frame.copy()
    sobel_vertical = np.float32([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_horizontal = np.transpose(sobel_vertical)
    sobel_vertical = cv2.filter2D(np.float32(copy1), -1, sobel_vertical)
    sobel_horizontal = cv2.filter2D(np.float32(copy2), -1, sobel_horizontal)
    sobel = np.sqrt(sobel_vertical * sobel_vertical + sobel_horizontal * sobel_horizontal)
    sobel = cv2.convertScaleAbs(sobel)
    cv2.imshow('Sobel', sobel)

    # ex8
    threshold_value = int(255 / 2)
    ret, binarized_frame = cv2.threshold(sobel, threshold_value, 255, cv2.THRESH_BINARY)
    cv2.imshow('Binarized', binarized_frame)

    # ex9
    lines_frame = binarized_frame.copy()
    nr_of_col = int(0.05 * lines_frame.shape[1])
    lines_frame[:, :nr_of_col] = 0  # left
    lines_frame[:, -nr_of_col:] = 0  # right

    indexes = np.argwhere(lines_frame > 1)
    midpoint = int(lines_frame.shape[1] / 2)
    left_indexes = indexes[indexes[:, 1] < midpoint]
    right_indexes = indexes[indexes[:, 1] >= midpoint]

    left_xs, left_ys = left_indexes[:, 1], left_indexes[:, 0]
    right_xs, right_ys = right_indexes[:, 1] - midpoint, right_indexes[:, 0]

    # ex10

    # left_line = np.polynomial.polynomial.polyfit(left_xs, left_ys, deg=1)
    # right_line = np.polynomial.polynomial.polyfit(right_xs, right_ys, deg=1)
    if left_xs.size > 0 and left_ys.size > 0:
        left_line = np.polynomial.polynomial.polyfit(left_xs, left_ys, deg=1)
    else:
        print("left_xs or left_ys is empty.")

    if right_xs.size > 0 and right_ys.size > 0:
        right_line = np.polynomial.polynomial.polyfit(right_xs, right_ys, deg=1)
    else:
        print("right_xs or right_ys is empty.")

    b = left_line[0]
    a = left_line[1]
    left_top_y = new_height
    left_top_x = (left_top_y - b) / a
    left_bottom_y = 0
    left_bottom_x = -b / a

    d = right_line[0]
    c = right_line[1]
    right_top_y = new_height
    right_top_x = (right_top_y - d) / c + int(new_width / 2)
    right_bottom_y = 0
    right_bottom_x = -d / c + int(new_width / 2)

    if int(new_width / 2) >= left_top_x >= 0 and int(new_width / 2) >= left_bottom_x >= 0:
        left_top_point = int(left_top_x), int(left_top_y)
        left_bottom_point = int(left_bottom_x), int(left_bottom_y)

    if new_width >= right_top_x >= int(new_width / 2) and new_width >= right_bottom_x >= int(new_width / 2):
        right_top_point = int(right_top_x), int(right_top_y)
        right_bottom_point = int(right_bottom_x), int(right_bottom_y)

    lines = cv2.line(lines_frame, left_bottom_point, left_top_point, (200, 0, 0), 5)
    lines = cv2.line(lines, right_bottom_point, right_top_point, (100, 0, 0), 5)
    lines = cv2.line(lines, (int(new_width / 2), 0), (int(new_width / 2), new_height), (255, 0, 0), 1)

    cv2.imshow('Lines', lines)

    # ex11
    blank = np.zeros((new_height, new_width), dtype=np.uint8)
    cv2.line(blank, left_top_point, left_bottom_point, (255, 0, 0), 3)

    magic_matrix = cv2.getPerspectiveTransform(trapezoid_bounds, pts)
    final_left = cv2.warpPerspective(blank, magic_matrix, (new_width, new_height))

    cv2.imshow('Final Left', final_left)

    left_lane = np.argwhere(final_left > 1)
    left_xs, left_ys = left_lane[:, 1], left_lane[:, 0]

    blank = np.zeros((new_height, new_width), dtype=np.uint8)
    cv2.line(blank, right_top_point, right_bottom_point, (255, 0, 0), 3)

    magic_matrix = cv2.getPerspectiveTransform(trapezoid_bounds, pts)
    final_right = cv2.warpPerspective(blank, magic_matrix, (new_width, new_height))

    cv2.imshow('Final Right', final_right)

    right_lane = np.argwhere(final_right > 1)
    right_xs, right_ys = right_lane[:, 1], right_lane[:, 0]

    # ex12
    final = resized_frame.copy()
    final[final_left > 0] = (50, 50, 250)
    final[final_right > 0] = (50, 250, 50)

    cv2.imshow('Final', final)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
