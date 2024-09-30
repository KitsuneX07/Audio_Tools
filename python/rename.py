import os


def rename(folder_path, index):
    for filename in os.listdir(folder_path):
        if filename.endswith(".svp"):
            new_filename = f"{index}_{filename}"
            index += 1
            os.rename(
                os.path.join(folder_path, filename),
                os.path.join(folder_path, new_filename),
            )
            print(f"文件已重命名: {filename} -> {new_filename}")


def rename_folder(folder_path):
    for folder in os.listdir(folder_path):
        folder_full_path = os.path.join(folder_path, folder)
        if os.path.isdir(folder_full_path):
            new_folder_name = folder.replace('song', 'audio')
            new_folder_full_path = os.path.join(folder_path, new_folder_name)
            os.rename(folder_full_path, new_folder_full_path)
            print(f"文件夹已重命名: {folder} -> {new_folder_name}")

if __name__ == "__main__":
    folder_path = r"D:\temp\dataset_reverb\output"  # 修改为你的文件夹路径
    rename_folder(folder_path)
