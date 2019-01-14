# Script for downloading all GLUE data, which is not in SentEval already. MNLI processed differently.

import os
import sys
import shutil
import argparse
import tempfile
import urllib.request
import zipfile

TASKS = ["CoLA", "QQP", "MNLI", "QNLI", "RTE", "WNLI", "diagnostic"]
TASK2PATH = {"CoLA":'https://firebasestorage.googleapis.com/v0/b/mtl-sentence-representations.appspot.com/o/data%2FCoLA.zip?alt=media&token=46d5e637-3411-4188-bc44-5809b5bfb5f4',
             "QQP":'https://firebasestorage.googleapis.com/v0/b/mtl-sentence-representations.appspot.com/o/data%2FQQP.zip?alt=media&token=700c6acf-160d-4d89-81d1-de4191d02cb5',
             "MNLI":'https://firebasestorage.googleapis.com/v0/b/mtl-sentence-representations.appspot.com/o/data%2FMNLI.zip?alt=media&token=50329ea1-e339-40e2-809c-10c40afff3ce',
             "QNLI":'https://firebasestorage.googleapis.com/v0/b/mtl-sentence-representations.appspot.com/o/data%2FQNLI.zip?alt=media&token=c24cad61-f2df-4f04-9ab6-aa576fa829d0',
             "RTE":'https://firebasestorage.googleapis.com/v0/b/mtl-sentence-representations.appspot.com/o/data%2FRTE.zip?alt=media&token=5efa7e85-a0bb-4f19-8ea2-9e1840f077fb',
             "WNLI":'https://firebasestorage.googleapis.com/v0/b/mtl-sentence-representations.appspot.com/o/data%2FWNLI.zip?alt=media&token=068ad0a0-ded7-4bd7-99a5-5e00222e0faf',
             "diagnostic":'https://storage.googleapis.com/mtl-sentence-representations.appspot.com/tsvsWithoutLabels%2FAX.tsv?GoogleAccessId=firebase-adminsdk-0khhl@mtl-sentence-representations.iam.gserviceaccount.com&Expires=2498860800&Signature=DuQ2CSPt2Yfre0C%2BiISrVYrIFaZH1Lc7hBVZDD4ZyR7fZYOMNOUGpi8QxBmTNOrNPjR3z1cggo7WXFfrgECP6FBJSsURv8Ybrue8Ypt%2FTPxbuJ0Xc2FhDi%2BarnecCBFO77RSbfuz%2Bs95hRrYhTnByqu3U%2FYZPaj3tZt5QdfpH2IUROY8LiBXoXS46LE%2FgOQc%2FKN%2BA9SoscRDYsnxHfG0IjXGwHN%2Bf88q6hOmAxeNPx6moDulUF6XMUAaXCSFU%2BnRO2RDL9CapWxj%2BDl7syNyHhB7987hZ80B%2FwFkQ3MEs8auvt5XW1%2Bd4aCU7ytgM69r8JDCwibfhZxpaa4gd50QXQ%3D%3D'}


def download_and_extract(task, data_dir):
    print("Downloading and extracting %s..." % task)
    data_file = "%s.zip" % task
    urllib.request.urlretrieve(TASK2PATH[task], data_file)
    with zipfile.ZipFile(data_file) as zip_ref:
        zip_ref.extractall(data_dir)
    os.remove(data_file)
    print("\tCompleted!")


def download_diagnostic(data_dir):
    print("Downloading and extracting diagnostic...")
    if not os.path.isdir(os.path.join(data_dir, "diagnostic")):
        os.mkdir(os.path.join(data_dir, "diagnostic"))
    data_file = os.path.join(data_dir, "diagnostic", "diagnostic.tsv")
    urllib.request.urlretrieve(TASK2PATH["diagnostic"], data_file)
    print("\tCompleted!")
    return


def get_tasks(task_names):
    task_names = task_names.split(',')
    if "all" in task_names:
        tasks = TASKS
    else:
        tasks = []
        for task_name in task_names:
            assert task_name in TASKS, "Task %s not found!" % task_name
            tasks.append(task_name)
    return tasks


def main(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='directory to save data to', type=str, default='.')
    parser.add_argument('--tasks', help='tasks to download data for as a comma separated string',
                        type=str, default='all')
    args = parser.parse_args(arguments)

    if not os.path.isdir(args.data_dir):
        os.mkdir(args.data_dir)
    tasks = get_tasks(args.tasks)

    for task in tasks:
        if task == 'diagnostic':
            download_diagnostic(args.data_dir)
        else:
            download_and_extract(task, args.data_dir)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))