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


if __name__ == "__main__":
    folder_path = f"D:\projects\python\diffsinger\sv_datasets\svp"
    index = 1
    rename(folder_path, index)
