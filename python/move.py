import os, shutil


def move(src_folder, dst_folder, target_format):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file.endswith(target_format):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dst_folder, file)
                shutil.move(src_path, dst_path)
                print(f"文件已移动: {src_path} -> {dst_path}")


if __name__ == "__main__":
    src_folder = r"D:\download\idm\IR"
    dst_folder = r".\data\IR"
    target_format = ".wav"
    move(src_folder, dst_folder, target_format)
