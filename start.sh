#!/bin/bash

python setup.py create-tasks /app/data

python setup.py run-studio --project-name "captcha-label" --data-dir /app/data_dir

exec python setup.py run-studio --project-name "captcha-label" --data-dir /app/data_dir