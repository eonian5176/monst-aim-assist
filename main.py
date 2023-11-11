from helpers import get_border_coords, view_img_with_border


with open("logs.txt", "w"):
    pass

coords = get_border_coords("imgs", scale= 1/2.5)

view_img_with_border("imgs/R.jpg", coords, scale = 1/2.5)