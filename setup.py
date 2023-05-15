import json
import pandas as pd
import psutil
import typer
import os
import subprocess
import logging
import sys

log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# log to setup.log
file_handler = logging.FileHandler("setup.log")
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

# log to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)


cli = typer.Typer()


def get_path_prefix(path1: str, path2: str) -> str:
    """
    Returns the path that is not common in the two input paths.
    """
    # Split the two paths into directories
    dirs1, dirs2 = path1.split("/"), path2.split("/")

    # Find the common directories
    common_dirs = [
        dirs1[i] for i in range(min(len(dirs1), len(dirs2))) if dirs1[i] == dirs2[i]
    ]

    # Build the extra path from the remaining directories of path1
    extra_path = "/" + "/".join(dirs1[len(common_dirs) :])

    if not extra_path.endswith("/"):
        extra_path += "/"

    return extra_path


def check_if_first_run(path: str = "config/init"):
    if os.path.exists(path):
        return False
    else:
        os.system("touch config/init")
        return True


@cli.command()
def create_tasks(
    input_dir: str = typer.Argument(help="Input directory, where images are stored"),
    pre_annotations: str = typer.Option(None, help="Path to pre-annotations file"),
    local_files_document_root: str = typer.Option(
        os.getcwd(), help="Same as `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT`"
    ),
    output_dir: str = typer.Option(
        None, help="Output directory, where tasks will be stored", hidden=True
    ),
):
    """
    Generates .json file for importing into LabelStudio.\n
        output_dir (str, optional): Output directory. Defaults to Input directory.
    """

    if output_dir is None:
        output_dir = input_dir
    else:
        os.makedirs(output_dir, exist_ok=True)

    images = [f for f in os.listdir(input_dir) if f.endswith(".png")]
    prefix = get_path_prefix(input_dir, local_files_document_root)

    for image in images:
        task = {"data": {"image": "/data/local-files/?d=" + prefix + image}}

        with open(
            os.path.join(
                output_dir, f'{image.split("/")[-1].replace(".png", "")}.json'
            ),
            "w",
        ) as f:
            json.dump(task, f, indent=2)

    logging.info(
        f"Dataset Abolute path: {os.path.join(local_files_document_root, output_dir)}"
    )
    logging.info(f"File Filter Regex: .*json")


@cli.command()
def run_studio(
    project_name: str = "captcha-recognition",
    label_config: str = "config/label-config.xml",
    local_files_serving_enabled: bool = True,
    local_files_document_root: str = os.getcwd(),
    data_dir: str = None,
):
    """
    Runs LabelStudio locally.
    """
    if check_if_first_run():
        command = [
            "label-studio",
            "init",
            project_name,
            "-b",
            "-l",
            label_config,
            "--username",
            os.getenv('USERNAME', "admin@localhost"),
            "--password",
            os.getenv('PASSWORD', "admin")
        ]
    else:
        command = [
            "label-studio",
            "start",
            project_name,
            "-b"
        ]


    if data_dir is not None:
        os.makedirs(data_dir, exist_ok=True)
        command.append("--data-dir")
        command.append(data_dir)


    logging.info(" ".join(command))
    env = {}
    if local_files_serving_enabled:
        env["LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED"] = "true"

        if local_files_document_root:
            env["LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT"] = local_files_document_root

    if os.getenv("VIRTUAL_ENV"):
        executable = os.path.join(os.environ["VIRTUAL_ENV"], "bin", "label-studio")
        subprocess.run(
            command,
            env=env,
            cwd=local_files_document_root,
            executable=executable,
            check=True,
        )
    else:
        executable = subprocess.run('which label-studio', shell=True, capture_output=True).stdout.decode('utf-8').strip()

        subprocess.run(
            command,
            env=env,
            cwd=local_files_document_root,
            executable=executable,
            check=True,
        )


@cli.command()
def generate_csv(dataset: str = typer.Argument(help="Exported project annotations from label-studio, use JSON-MIN format while exporting"), output: str = typer.Option("data/dataset.csv", help="Path to generated CSV file")):
    """
    Generates .csv file for generating TFRecords.
    """
    collumns = ["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"]
    captcha_data = []

    with open(dataset, "r") as _buf:
        dataset = json.loads(_buf.read())

    for el in dataset:
        try:
            classes = list(el["solved_captcha"])
            i = 0

            for _class in classes:

                captcha_data.append(
                    (
                        el["image"].split("/")[-1],
                        el["box"][i]["original_width"],
                        el["box"][i]["original_height"],
                        _class,
                        round(el["box"][i]["x"]),
                        round(el["box"][i]["y"]),
                        round(el["box"][i]["x"] + el["box"][i]["width"]),
                        round(el["box"][i]["y"] + el["box"][i]["height"]),
                    )
                )
                i += 1
        except KeyError as e:
            logging.error(
                f'KeyError: id => {el["id"]}, image => { el["image"].replace("/data/local-files/?d=/", "")}'
            )
    df = pd.DataFrame(captcha_data, columns=collumns)
    df.to_csv(output, index=None)
    logging.info(f"Generated {output}")


if __name__ == "__main__":
    cli()
