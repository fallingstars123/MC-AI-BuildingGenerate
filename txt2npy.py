import numpy as np
from Map import rotate_block, rotate_attr_vector, mirror_block, mirror_attr_vector
from mc_data_utils import parse_short

input_file = "parsed_block_data.txt"
output_file = "block_data_.npy"

blocks_original, blocks_90, blocks_180, blocks_270, blocks_mirror_north_south, blocks_mirror_east_west = [], [], [], [], [], []

def get_unique_arrays(arrays):
    """返回独特数组的数组（使用哈希表优化）"""
    seen = set()
    unique_arrays = []
    for arr in arrays:
        arr_hashable = tuple(map(tuple, arr))  # 将数组转换为可哈希的元组
        if arr_hashable not in seen:
            unique_arrays.append(arr)
            seen.add(arr_hashable)
    return unique_arrays

with open('metadata.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    width, height, length = map(parse_short, lines[0].strip().split(','))
    
# 解析文本文件
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = eval(line)
        x, y, z, (block_type, subtype, attr_vector) = parts

        # 存储原始方块数据
        blocks_original.append([x, y, z, block_type, subtype] + attr_vector)

        # 旋转、镜像处理
        for angle in [90, 180, 270]:
            new_x, new_y, new_z = rotate_block(x, y, z, angle, width-1, length-1)
            new_attr_vector = rotate_attr_vector(block_type, attr_vector.copy(), angle)
            locals()[f"blocks_{angle}"].append([new_x, new_y, new_z, block_type, subtype] + new_attr_vector)

        for direction in ["north_south", "east_west"]:
            new_x, new_y, new_z = mirror_block(x, y, z, direction, width-1, length-1)
            new_attr_vector = mirror_attr_vector(block_type, attr_vector.copy(), direction)
            locals()[f"blocks_mirror_{direction}"].append([new_x, new_y, new_z, block_type, subtype] + new_attr_vector)

arrays = [blocks_original, blocks_90, blocks_180, blocks_270, blocks_mirror_north_south, blocks_mirror_east_west]
# 按 (x, y, z) 排序每个数组
for i in range(len(arrays)):
    arrays[i] = sorted(arrays[i], key=lambda block: (block[0], block[1], block[2]))

# 转换为 NumPy 数组方便比较
original_array = np.array(blocks_original, dtype=np.int32)
mirror_north_south_array = np.array(blocks_mirror_north_south, dtype=np.int32)
mirror_east_west_array = np.array(blocks_mirror_east_west, dtype=np.int32)

# 按坐标排序，确保顺序一致（不然即使内容一样，顺序不同也会显示差异）
original_array = original_array[np.lexsort(original_array[:, :3].T)]
mirror_north_south_array = mirror_north_south_array[np.lexsort(mirror_north_south_array[:, :3].T)]
mirror_east_west_array = mirror_east_west_array[np.lexsort(mirror_east_west_array[:, :3].T)]

# 找出差异
diff = original_array != mirror_east_west_array

# # 打印不同的行
# if not np.array_equal(original_array, mirror_east_west_array):
#     for i in range(len(original_array)):
#         if not np.array_equal(original_array[i], mirror_east_west_array[i]):
#             print(f"原数组: {original_array[i]}")
#             print(f"东西镜像后: {mirror_east_west_array[i]}")
# else:
#     print("原数组与东西镜像后的数组完全一致！")

if not np.array_equal(original_array, mirror_north_south_array):
    for i in range(len(original_array)):
        if not np.array_equal(original_array[i], mirror_north_south_array[i]):
            print(f"原数组: {original_array[i]}")
            print(f"南北镜像后: {mirror_north_south_array[i]}")
else: 
    print("原数组与南北镜像后的数组完全一致！")

unique_arrays = get_unique_arrays(arrays)

for i, array in enumerate(unique_arrays):
    array = np.array(array, dtype=np.int32)
    max_x, max_y, max_z = array[:, 0].max(), array[:, 1].max(), array[:, 2].max()
    structure = np.full((max_x + 1, max_y + 1, max_z + 1, 7), -1, dtype=np.int32)

    for x, y, z, block_type, subtype, *attr_vector in array:
        structure[x, y, z] = [block_type, subtype] + attr_vector

    np.save(f"block_data_{i}.npy", structure)
    print(f"数据成功保存到 block_data_{i}.npy，形状为 {structure.shape}")
