import os

import numpy as np
import cv2

import logging

logging.basicConfig(level = logging.INFO, filename = "logs.txt", filemode = "a")

logger = logging.getLogger(__name__)


def find_border(img_path: str, scale: int) -> dict[str, tuple[int, int]]:
    """
    img_path: path to image borders (4 images of name L, U, R, D) in jpg format
    scale: multiplier to scale up image for PC view, e.g. 2 for expand 2x
    """
    coordinates = {}

    def click_event(event, x: int, y: int, flags: int, param: tuple[str, np.ndarray]) -> None:
        edge, old_img = param
        if event == cv2.EVENT_LBUTTONDOWN:
            img = old_img.copy()
            coordinates[edge] = (x, y)
            cv2.circle(img, (x, y), 5, (255, 0, 0), -1)  # Draw dot where user clicked
            cv2.imshow(f"{edge}", img)
            logger.info(f"Selected coordinate: ({x},{y})")

    for edge in ["L", "U", "R", "D"]:
        img = cv2.imread(os.path.join(img_path, f"{edge}.jpg"))

        #print(img.shape)
        #samsung s21 has 2340x1080, gcd of 180. scaled down by 3x
        scaled_sz = (int(img.shape[1] * scale), int(img.shape[0] * scale))
        img = cv2.resize(img, scaled_sz, interpolation = cv2.INTER_LINEAR)
        cv2.imshow(f"{edge}", img)
        
        # Set mouse callback function for window
        cv2.setMouseCallback(edge, click_event, (edge, img))
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return coordinates

def scale_border_coords(raw_coords: dict[str, tuple[int, int]], scale: int) -> dict[str, int]:
    """returns left, right, up, down border of screen to new scale"""
    new_coords = {}
    
    new_coords["L"] = int(raw_coords["L"][0]*scale)
    new_coords["R"] = int(raw_coords["R"][0]*scale)
    new_coords["U"] = int(raw_coords["U"][1]*scale)
    new_coords["D"] = int(raw_coords["D"][1]*scale)
    
    return new_coords

def get_border_coords(img_path: str, scale: int) -> dict[str, int]:
    """
    combines the 2 function above to get left, right up, down border
    """
    rel_coords = find_border(img_path, scale)
    return scale_border_coords(rel_coords, 1/scale)


def draw_border(image: np.ndarray, coords: dict[str, int], color: tuple[int, int, int], thickness: int=10):
    """
    returns copy of image with border in it
    """
    img_copy = image.copy()
    cv2.line(img_copy, (coords['L'], coords['U']), (coords['L'], coords['D']), color, thickness)
    cv2.line(img_copy, (coords['R'], coords['U']), (coords['R'], coords['D']), color, thickness)
    cv2.line(img_copy, (coords['L'], coords['U']), (coords['R'], coords['U']), color, thickness)
    cv2.line(img_copy, (coords['L'], coords['D']), (coords['R'], coords['D']), color, thickness)

    return img_copy


def view_img_with_border(img_path: str, coords: dict[str, int], scale: int) -> None:
    """
    returns image of monst gameplay with border
    img_path: img of monst gameplay
    coords: coordinates of border L,R,U,D dict
    scale: scale to expand image for better view on PC
    """
    img = cv2.imread(img_path)

    img = draw_border(img, coords, (255, 255, 255))

    scaled_sz = (int(img.shape[1] * scale), int(img.shape[0] * scale))
    img = cv2.resize(img, scaled_sz, interpolation = cv2.INTER_LINEAR)

    cv2.imshow("bordered", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
