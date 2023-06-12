import asyncio
import logging as log
import os
from platform import platform
import sys
from PIL import Image
from io import BytesIO
from httpx import  AsyncClient
from os import getcwd, makedirs, path, getenv, walk

log_formatter = log.Formatter("%(asctime)s [%(levelname)s] %(message)s")
root_logger = log.getLogger()
root_logger.setLevel(log.INFO)

# log to setup.log
file_handler = log.FileHandler("setup.log")
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

# log to stdout
console_handler = log.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

USERNAME = getenv("USER") if getenv("USER") else input("Input username: ")
IMAGE_DIR = str
SAVE_DIR = str
CLASS_FILE = 'class/alphabets.txt'

async def main():
    global IMAGE_DIR, SAVE_DIR
    
    if path.exists("image/" + USERNAME):
        log.info(f"image/{USERNAME} already exists")
    else:
        makedirs("image/" + USERNAME, exist_ok=True)
        makedirs("save/" + USERNAME, exist_ok=True)

        log.info(f"image/{USERNAME} created")

    IMAGE_DIR = path.join(getcwd(), "image/" + USERNAME)
    SAVE_DIR = path.join(getcwd(), "save/" + USERNAME)

    start = 0

    for dirname, _, filenames in walk(IMAGE_DIR):
        try:
            start = int(filenames[-1].removeprefix("captcha_").removesuffix(".png")) + 1
        except IndexError:
            start = 0
    
    stop  = start + 100

    for i in range(start, stop):
        async with AsyncClient() as client:
            response = await client.get("https://javdb.com/rucaptcha")
            img = Image.open(BytesIO(response.content))
            img.save(path.join(IMAGE_DIR, f"captcha_{i}.png"), "PNG", optimize=True, quality=100, )

    if platform() == "win32":
        log.info(f"RUN: ./bin/labelImg.exe {IMAGE_DIR} {CLASS_FILE}")
    else:
         log.info('RUN: python labelImg/labelImg.py {} {}'.format(IMAGE_DIR, CLASS_FILE))


if __name__ == "__main__":
    asyncio.run(main())
   
