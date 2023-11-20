import json
from helpers import (
    get_border_coords, 
    view_img_with_border, 
    store_coords, 
    calculate_trajectory,
    get_starting_position,
    view_img_with_trajectories,
)


#for now, please set this flag to let the program know if your border is set.
border_set = True

while not border_set:
    coords = get_border_coords("borders", scale= 1/2.5)

    for side in {"L", "U", "R", "D"}:
        view_img_with_border(f"borders/{side}.jpg", coords, scale = 1/2.5)

    confirm_border = input("Is the border set correctly? (y/n): ")

    if confirm_border == "y":
        border_set = True
        store_coords(coords)


with open("border.json", "r") as border_file:
    border = json.load(border_file)

start = get_starting_position("current/shot.jpg", scale = 1/2.5)

trajectories = calculate_trajectory(start, 141, border)
view_img_with_trajectories("current/shot.jpg", trajectories, border, scale=1/2.5)

