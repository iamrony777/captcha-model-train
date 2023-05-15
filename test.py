import json
import cv2 as cv


# with open('export.json', 'r') as f:
#     data = json.load(f)

#     for i in data:
#         image_path = i['image'].replace('/data/local-files/?d=/', '')
#         image = cv.imread(image_path)

#         cv.namedWindow(image_path, cv.WINDOW_NORMAL)
#         cv.setWindowProperty(image_path, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

#         for c in i['box']:
#             x, y, w, h = round(c['x']), round(c['y']), round(c['width']), round(c['height'])
#             cv.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)


#         cv.imshow(image_path,image)
#         k = cv.waitKey(0)

#         if k == ord('q'):
#             cv.destroyAllWindows(image_path)


img = cv.imread("data/aaadh.png")

y = 13
x = 35
w = 12
h = 43

# x = 31
# y = 18
# w = 18
# h = 40


top_left = (x, y)
bottom_right = (x + w, y + h)

cv.rectangle(img, top_left, bottom_right, color=(255, 255, 0), thickness=2)

cv.imshow("captcha", img)
k = cv.waitKey(0)

if k == ord("q"):
    cv.destroyAllWindows()
