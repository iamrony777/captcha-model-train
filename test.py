import os

for dirname, _, filenames in os.walk('image/rony'):
    print(filenames[-1].removeprefix("captcha_").removesuffix(".png"))
    # for filename in filenames:
    #     print(os.path.join('./', dirname, filename))