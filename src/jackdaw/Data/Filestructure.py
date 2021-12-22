import os
import shutil

DATA_DIR = "ProjectData"


def delete_project_in_current_dir():
    if os.path.isdir(DATA_DIR):
        shutil.rmtree(DATA_DIR)
