import os
import shutil


def clear_design_docs():
    base_path = "design_docs"
    if os.path.exists(base_path):
        for name in os.listdir(base_path):
            path = os.path.join(base_path, name)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                print(f"Failed to delete {path}: {e}")
