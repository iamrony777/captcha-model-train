from json import loads
import logging
import sys

import cv2 as cv
import pandas as pd

log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# log to setup.log
# file_handler = logging.FileHandler("setup.log")
# file_handler.setFormatter(log_formatter)
# root_logger.addHandler(file_handler)

# log to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

collumns = ["id", "filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"]

def select_element(_captcha, box):
    selected_elements = []
    for i, b in enumerate(box):
        x = b["x"]
        y = b["y"]
        w = b["width"]
        h = b["height"]
        selected_elements.append(
            (
                b["original_width"],
                b["original_height"],
                _captcha[i],
                round(x * b["original_width"] / 100),
                round(y * b["original_height"] / 100),
                round(w * b["original_width"] / 100),
                round(h * b["original_height"] / 100),
            )
        )
    return selected_elements


with open("project-1-at-2023-05-15-06-03-bb0e37b4.json") as _buf:
    raw = loads(_buf.read())
    data = []
    logging.info(f" Total completed annotaions :{len(raw)}")

    for d in raw:
        _filename = d["image"].split("/")[-1]
        _filepath = d["image"].replace("/data/local-files/?d=/", "")
        _id = d["id"]
        _captcha = list(d["solved_captcha"])

        for el in select_element(_captcha, d["box"]):
            w,h,c,xmin,ymin,xmax,ymax = el
            img = cv.imread(_filepath)


            top_left = (xmin, ymin)
            bottom_right = (xmin + xmax, ymin + ymax)

            cv.rectangle(img, top_left, bottom_right, color=(255, 0, 0), thickness=2)
            _filepath = f"data/cv/{_filename}_{_id}.png"
            cv.imwrite(_filepath, img)
        cv.imshow("captcha", img)
        k = cv.waitKey(0)

        if k == ord("q"):
            cv.destroyAllWindows()


# df = pd.DataFrame(data, columns=collumns)
# df.to_csv("dataset.csv", index=None)