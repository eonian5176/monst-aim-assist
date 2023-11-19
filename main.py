import json
from helpers import get_border_coords, view_img_with_border, store_coords, calculate_trajectory


#for now, please set this flag to let the program know if your border is set.
border_set = True

while not border_set:
    coords = get_border_coords("imgs", scale= 1/2.5)

    view_img_with_border("imgs/R.jpg", coords, scale = 1/2.5)

    confirm_border = input("Is the border set correctly? (y/n): ")

    if confirm_border == "y":
        border_set = True
        store_coords(coords)


with open("border.json", "r") as border_file:
    border = json.load(border_file)
    print(calculate_trajectory((500, 500), 10, border))