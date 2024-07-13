import os
import json

regen_data_path = "world/project-regen/"

def get_files(folder_path: str) -> list[str]:
    if not os.path.exists(folder_path):
        return []

    files_paths: list[str] = []
    for files in os.listdir(folder_path):
        files_paths.append(os.path.join(folder_path, files))

    return files_paths


if __name__ == "__main__":
    regen_data_files = get_files(folder_path=regen_data_path)

    for regen_data_file in regen_data_files:
        if not regen_data_file.endswith(".jsonl"):
            continue

        print("Cleaning up regions in %s..." % regen_data_file)
        print("-"*40)
        with open(regen_data_file, mode="r") as file:
            while True:
                line = file.readline()

                # EOF
                if not line:
                    break

                record = json.loads(line)

                if record["safe"] == False and record["force_safe"] == False:
                    print("Removing %s..." % record["path"])
                    os.remove(record["path"])