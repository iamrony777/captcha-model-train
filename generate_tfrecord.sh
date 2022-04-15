#!/bin/bash

python3 generate_tfrecord.py --csv_input=train_labels.csv --image_dir=train --output_path=train.record

python3 generate_tfrecord.py --csv_input=test_labels.csv --image_dir=test --output_path=test.record
