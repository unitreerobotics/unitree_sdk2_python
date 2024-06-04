import os,sys


def check_init_files(directory):
    """递归确认包存在__init__.py防止缺胳膊少腿"""
    all_dirs_have_init = True
    for root, dirs, files in os.walk(directory):
        if "__pycache__" in dirs:
            dirs.remove("__pycache__") 
        if "test" in dirs:
            dirs.remove("test")
        if "__init__.py" not in files:
            print(f"Directory '{root}' is missing '__init__.py'")
            all_dirs_have_init = False
    return all_dirs_have_init

directory_to_check = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","unitree_sdk2py")
if check_init_files(directory_to_check):
    print("所有文件夹均含 '__init__.py'.")
else:
    print("校验未通过", file=sys.stderr)