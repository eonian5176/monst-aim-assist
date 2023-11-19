import os
import math

import json

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
    Once the user set up a folder with 4 images (named L/U/R/D.jpg), pass the
    folder as img_path to set border

    img_path: Path to the 4 border images
    scale: scale to view the images at

    returns - Dictionary with 4 elements L, U, R, D, each referencing a pixel
    position for the respective side
    """
    rel_coords = find_border(img_path, scale)
    return scale_border_coords(rel_coords, 1/scale)


def store_coords(coords: dict[str, int], store_path: str = os.getcwd()) -> None:
    """
    stores coordinates of border into json file for reference during gameplay
    """
    if not os.path.exists(store_path):
        os.makedirs(store_path)

    with open(os.path.join(store_path, "border.json"), 'w') as file:
        json.dump(coords, file)


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



def calculate_trajectory(start_pos: tuple[int, int], shot_angle: int, border: dict[str, int], reflect_limit: int = 10) -> list[tuple[int, int]]:
    """
    start_x, start_y: starting position for current unit
    shot_angle: angle of shot in degrees (0-359), 0 referencing --> direction
    border: location of border, dict[str, int]
    reflections: number of reflections to compute, e.g. 1 means stop when hit 1 wall
    """

    #preset values
    x, y = start_pos
    angle = shot_angle * math.pi/180
    step = 0.1 #step size to take in given direction in pixel

    #calculate process
    points: list[tuple[int, int]] = [start_pos]

    while len(points) <= reflect_limit+1:
        # Calculate next position based on current_angle
        x += step*math.cos(angle)
        y += step*math.sin(angle)

        # Check if the new position hits any border
        border_hit = check_border_hit(x, y, border)
        if border_hit:
            angle = get_reflected_angle(angle, border_hit)
            points.append((round(x), round(y)))

    return points

def check_border_hit(x: float, y: float, border: tuple[str, int]) -> str:
    """
    First check for 2 border cases, then check for single border hit.
    
    Returns: empty string if no border hit, '2' if 2 borders hit, or otherwise the
    corresponding border hit.
    """
    border_hit = ""
    num_hit = 0

    if x < border["L"]:
        border_hit = "L"
        num_hit += 1

    if x > border["R"]:
        border_hit = "R"
        num_hit += 1

    if y < border["U"]:
        border_hit = "U"
        num_hit += 1

    if y > border["D"]:
        border_hit = "D"
        num_hit += 1

    if num_hit == 2:
        border_hit = "2"


    if num_hit > 2:
        raise ValueError("Error, more than 2 borders hit at the same time")

    return border_hit

def get_reflected_angle(angle: float, border_hit: str):
    """
    for why these angles work, see:
    https://math.libretexts.org/Bookshelves/Precalculus/Elementary_Trigonometry_(Corral)/01%3A_Right_Triangle_Trigonometry_Angles/1.05%3A_Rotations_and_Reflections_of_Angles

    where instead of a simple reflection on incident axis, we reflect its opposite direction path through the other axis
    """
    if border_hit in {"L", "R"}:
        return math.pi-angle
    
    if border_hit in {"U", "D"}:
        return -angle
    
    if border_hit == "2":
        return angle + math.pi
    
