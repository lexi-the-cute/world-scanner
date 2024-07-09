import os
import sys
import anvil

from typing import Union, List

def get_dimension_folders(dimension_folder_root: str) -> list[str]:
    if not os.path.exists(dimension_folder_root):
        return []

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
    paths: list[str] = []

    # main world folder
    paths.append(get_region_folder(world_folder_root))

    # dimension folder paths
    dimensions: list[str] = get_dimension_folders(dimension_folder_root)
    for dimension_path in dimensions:
        paths.append(get_region_folder(dimension_path))

    return paths

def get_entity_folder(world_folder: str) -> str:
    return os.path.join(world_folder, "entities")

# this is an ease of use function
def get_entity_folders(world_folder_root: str, dimension_folder_root: str) -> list[str]:
    paths: list[str] = []

    # main world folder
    paths.append(get_entity_folder(world_folder_root))

    # dimension folder paths
    dimensions: list[str] = get_dimension_folders(dimension_folder_root)
    for dimension_path in dimensions:
        paths.append(get_entity_folder(dimension_path))

    return paths

def get_poi_folder(world_folder: str) -> str:
    return os.path.join(world_folder, "poi")

# this is an ease of use function
def get_poi_folders(world_folder_root: str, dimension_folder_root: str) -> list[str]:
    paths: list[str] = []

    # main world folder
    paths.append(get_poi_folder(world_folder_root))

    # dimension folder paths
    dimensions: list[str] = get_dimension_folders(dimension_folder_root)
    for dimension_path in dimensions:
        paths.append(get_poi_folder(dimension_path))

    return paths

def get_files(folder_path: str) -> list[str]:
    if not os.path.exists(folder_path):
        return []

    files_paths: list[str] = []
    for files in os.listdir(folder_path):
        files_paths.append(os.path.join(folder_path, files))

    return files_paths

def get_blocks_in_chunk(chunk: anvil.Chunk):
    # Read Palette Test
    # for section_y in range(chunk.lowest_y, chunk.highest_y):
    #     print("Palette %i: %s" % (section_y, chunk.get_palette(section_y)))

    for block_y in range(chunk.lowest_y*16, (chunk.highest_y*16)+15):
        for block_z in range(16):
            for block_x in range(16):
                yield chunk.get_block(block_x, block_y, block_z), block_x, block_y, block_z

def get_blocks(region_file_path: str, hidden_blocks: List[str] = []):
    try:
        region = anvil.Region.from_file(region_file_path)

        split_filename: List[str] = region_file_path.split("/")[-1].split(".")
        region_x: int = int(split_filename[1])
        region_z: int = int(split_filename[2])
        # print("Region: (%s, %s)" % (region_x, region_z))
    except anvil.errors.EmptyRegionFile as e:
        return

    for chunk_x in range(32):
        for chunk_z in range(32):
            try:
                chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
                for block, block_x, block_y, block_z in get_blocks_in_chunk(chunk):
                    if ("%s:%s" % (block.namespace, block.id)) not in hidden_blocks:
                        region_chunk_x: int = (32*region_x)+chunk_x
                        region_chunk_z: int = (32*region_z)+chunk_z

                        global_block_x: int = (16*region_chunk_x)+block_x
                        global_block_z: int = (16*region_chunk_z)+block_z

                        block_entity = chunk.get_block_entity(global_block_x, block_y, global_block_z)

                        yield global_block_x, block_y, global_block_z, block, block_entity
            except anvil.errors.ChunkNotFound as e:
                pass
            except anvil.errors.CorruptedData as e:
                # with open("corrupted.nbt", "wb") as corrupted_nbt_data:
                #     corrupted_nbt_data.write(e.args[0]['data'])

                print("CorruptedData: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e.args[0]['message']), file=sys.stderr)
            except anvil.errors.OutOfBoundsCoordinates as e:
                print("OutOfBoundsCoordinates: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)
            # except Exception as e:
            #     pass
            #     print("Exception: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)

def get_block_entities(region_file_path: str, hidden_blocks: List[str] = []):
    try:
        region = anvil.Region.from_file(region_file_path)
    except anvil.errors.EmptyRegionFile as e:
        return

    for chunk_x in range(32):
        for chunk_z in range(32):
            try:
                chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
                for block_entity in chunk.block_entities:
                    block_x: int = block_entity["x"].value
                    block_y: int = block_entity["y"].value
                    block_z: int = block_entity["z"].value
                    
                    # the chunk reader handles y for us as long as we don't specify a section
                    chunk_block_x: int = block_x % 16
                    chunk_block_z: int = block_z % 16

                    block: anvil.Block = chunk.get_block(x=chunk_block_x, y=block_y, z=chunk_block_z)

                    if ("%s:%s" % (block.namespace, block.id)) not in hidden_blocks:
                        # print("Global Coordinates: (%s, %s, %s) - Chunk Block Debug: (%s, %s, %s)" % (block_x, block_y, block_z, chunk_block_x, block_y, chunk_block_z))
                        yield block_x, block_y, block_z, block, block_entity
            except anvil.errors.ChunkNotFound as e:
                pass
            except anvil.errors.EmptyRegionFile as e:
                pass
            except anvil.errors.CorruptedData as e:
                # with open("corrupted.nbt", "wb") as corrupted_nbt_data:
                #     corrupted_nbt_data.write(e.args[0]['data'])

                print("CorruptedData: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e.args[0]['message']), file=sys.stderr)
            except anvil.errors.OutOfBoundsCoordinates as e:
                print("OutOfBoundsCoordinates: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)
            # except Exception as e:
            #     pass
            #     print("Exception: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)

# TODO: Implement entity scanning support
def get_entities(entity_file_path: str, hidden_entities: List[str] = []):
    try:
        region = anvil.Region.from_file(region_file_path)
    except anvil.errors.EmptyRegionFile as e:
        return

    for chunk_x in range(32):
        for chunk_z in range(32):
            try:
                chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)

                # TODO: Get entity data: https://minecraft.wiki/w/Entity_format
            except anvil.errors.ChunkNotFound as e:
                pass
            except anvil.errors.EmptyRegionFile as e:
                pass
            except anvil.errors.CorruptedData as e:
                # with open("corrupted.nbt", "wb") as corrupted_nbt_data:
                #     corrupted_nbt_data.write(e.args[0]['data'])

                print("CorruptedData: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e.args[0]['message']), file=sys.stderr)
            except anvil.errors.OutOfBoundsCoordinates as e:
                print("OutOfBoundsCoordinates: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)
            # except Exception as e:
            #     pass
            #     print("Exception: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)

# TODO: Implement points of interest scanning support
def get_pois(poi_file_path: str, hidden_pois: List[str] = []):
    try:
        region = anvil.Region.from_file(region_file_path)
    except anvil.errors.EmptyRegionFile as e:
        return

    for chunk_x in range(32):
        for chunk_z in range(32):
            try:
                chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)

                # TODO: Get poi data (stub): https://minecraft.wiki/w/Java_Edition_level_format#poi_format
            except anvil.errors.ChunkNotFound as e:
                pass
            except anvil.errors.EmptyRegionFile as e:
                pass
            except anvil.errors.CorruptedData as e:
                # with open("corrupted.nbt", "wb") as corrupted_nbt_data:
                #     corrupted_nbt_data.write(e.args[0]['data'])

                print("CorruptedData: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e.args[0]['message']), file=sys.stderr)
            except anvil.errors.OutOfBoundsCoordinates as e:
                print("OutOfBoundsCoordinates: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)
            # except Exception as e:
            #     pass
            #     print("Exception: %s (%s, %s): %s" % (region_file_path, chunk_x, chunk_z, e), file=sys.stderr)
