import os
import anvil

def get_dimension_folders(dimension_folder_root: str) -> list[str]:
    dimensions: list[str] = []
    for namespace in os.listdir(dimension_folder_root):
        namespace_path: str = os.path.join(dimension_folder_root, namespace)
        for path in os.listdir(namespace_path):
            dimensions.append(os.path.join(namespace_path, path))

    return dimensions

def get_region_folder(world_folder: str) -> str:
    return os.path.join(world_folder, "region")

# this is an ease of use function
def get_region_folders(world_folder_root: str, dimension_folder_root: str) -> list[str]:
    region_paths: list[str] = []

    # main world folder
    world_region_path: str = get_region_folder(world_folder_root)
    region_paths.append(world_region_path)

    # dimension folder paths
    dimensions: list[str] = get_dimension_folders(dimension_folder_root)
    for dimension_path in dimensions:
        region_paths.append(get_region_folder(dimension_path))

    return region_paths

def get_region_files(region_folder_path: str) -> list[str]:
    region_files_paths: list[str] = []
    for files in os.listdir(region_folder_path):
        region_files_paths.append(os.path.join(region_folder_path, files))

    return region_files_paths

def get_blocks(region_file_path: str):
    print("Reading Region file: %s" % region_file_path)
    print("-"*40)

    region = anvil.Region.from_file(region_file_path)

    for x in range(32):
        for y in range(32):
            try:
                chunk = anvil.Chunk.from_region(region, x, y)
                print("Reading from chunk (%i, %i)" % (x, y))
                block = chunk.get_block(0, 10, 0)

                print("Test Read Block: (%i, %i, %i): %s" % (0, 90, 0, block.id))
            except Exception as e:
                pass
                print("Exception: %s" % e)
    
    print("")
    print("-"*40)

if __name__ == "__main__":
    world_folder_root = "world"
    dimension_folder_root = os.path.join(world_folder_root, "dimensions")

    region_folders_paths: list[str] = get_region_folders(world_folder_root, dimension_folder_root)

    get_blocks("world/region/r.0.0.mca")
    # for region_folder_paths in region_folders_paths:
    #     region_files_paths: list[str] = get_region_files(region_folder_paths)

    #     for region_files_path in region_files_paths:
    #         get_blocks(region_files_path)