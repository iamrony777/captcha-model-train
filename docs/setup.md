# Setup

## Getting images and labeling them

> Download new captchas from here if required https://rucaptcha-proxy.vercel.app/


```bash
# Required python version 3.7.*
git clone https://github.com/iamrony777/captcha-model-train.git
cd captcha-model-train

# Setup python virtualenv and install packages
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements-utils.txt

```
### Create Tasks to start labeling images

```bash
python setup.py create-tasks <input-dir> 
```
* _input-dir_ : dataset location (captcha images)
* [optional] _--output-file_ : tasks.json
* [optional] _--local-files-document-root_ : Current directory


    > **tasks.json** example

    ```json
    [
    {
        "data": {
        "image": "/data/local-files/?d=/CAPTCHA_images/aaukm.png"
        }
    },
    {
        "data": {
        "image": "/data/local-files/?d=/CAPTCHA_images/cfhou.png"
        }
    },
    ...
    ]

    ```


### Run Label-Studio and start labeling images
```bash
python setup.py run-studio
```
