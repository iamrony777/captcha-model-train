"""
Usage:
  # In local folder
  # Create train data:
  python generate_tfrecord.py --csv_input=CSGO_images\train_labels.csv --image_dir=CSGO_images\train --output_path=CSGO_images\train.record

  # Create test data:
  python generate_tfrecord.py --csv_input=CSGO_images\test_labels.csv --image_dir=CSGO_images\test --output_path=CSGO_images\test.record
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import re
import cv2
import pandas as pd
import tensorflow as tf

from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict

# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

flags = tf.compat.v1.app.flags
flags.DEFINE_string("csv_input", "", "Path to the CSV input")
flags.DEFINE_string("image_dir", "", "Path to the image directory")
flags.DEFINE_string("output_path", "", "Path to output TFRecord")
FLAGS = flags.FLAGS


def class_text_to_int(_class):
    with open("data/tools/labelmap.pbtxt", "r") as f:
        curr_id = None
        for line in f:
            curr_id = (
                line.strip().split("id: ")[-1]
                if bool(re.search(r"id", line))
                else curr_id
            )

            if "name: '" + _class + "'" in line:
                return int(curr_id)
    # If we get here, the character was not found in the file
    return None


def split(df, group):
    data = namedtuple("data", ["filename", "object"])
    gb = df.groupby(group)
    return [
        data(filename, gb.get_group(x))
        for filename, x in zip(gb.groups.keys(), gb.groups)
    ]


def create_tf_example(group, path):
    image = cv2.imread(os.path.join(path, "{}".format(group.filename)))
    _, image_data = cv2.imencode(".png", image)
    image_bytes = image_data.tobytes()

    height, width, _ = image.shape

    filename = group.filename.encode("utf8")
    image_format = b"png"
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(round(row["xmin"] / width, 3))
        ymins.append(round(row["ymin"] / height, 3))
        xmaxs.append(round(row["xmax"] / width, 3))
        ymaxs.append(round(row["ymax"] / height, 3))
        classes_text.append(row["class"].encode("utf8"))
        classes.append(class_text_to_int(row["class"]))

    tf_example = tf.train.Example(
        features=tf.train.Features(
            feature={
                "image/height": dataset_util.int64_feature(height),
                "image/width": dataset_util.int64_feature(width),
                "image/filename": dataset_util.bytes_feature(filename),
                "image/source_id": dataset_util.bytes_feature(filename),
                "image/encoded": dataset_util.bytes_feature(image_bytes),
                "image/format": dataset_util.bytes_feature(image_format),
                "image/object/bbox/xmin": dataset_util.float_list_feature(xmins),
                "image/object/bbox/xmax": dataset_util.float_list_feature(xmaxs),
                "image/object/bbox/ymin": dataset_util.float_list_feature(ymins),
                "image/object/bbox/ymax": dataset_util.float_list_feature(ymaxs),
                "image/object/class/text": dataset_util.bytes_list_feature(
                    classes_text
                ),
                "image/object/class/label": dataset_util.int64_list_feature(classes),
            }
        )
    )
    return tf_example


def main(_):
    writer = tf.compat.v1.python_io.TFRecordWriter(FLAGS.output_path)
    path = os.path.join(os.getcwd(), FLAGS.image_dir)
    examples = pd.read_csv(FLAGS.csv_input, index_col=None)
    grouped = split(examples, "filename")
    for group in grouped:
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())

    writer.close()
    output_path = os.path.join(os.getcwd(), FLAGS.output_path)
    print("Successfully created the TFRecords: {}".format(output_path))


if __name__ == "__main__":
    tf.compat.v1.app.run()
    # print(class_text_to_int('z'))
