import numpy as np
import pyvista as pv
from nbtlib import File, Compound, Int, ByteArray, load
import re

# 定义方块类型和子类型映射
BLOCK_TYPE_MAP = {
    "log": 0,
    "planks": 1,
    "stairs": 2,
    "slab": 3,
    "fence": 4,
    "glass_pane": 5,
    "door": 6,
    "functional": 7,  # 比如箱子、工作台这种
    "grass_block": 8,
    "air": 9
}

STAIR_SUBTYPE_MAP = {
    "oak_stairs": 0,
    "dark_oak_stairs": 1,
    "birch_stairs": 2,
    "spruce_stairs": 3
}

def encode_block_data(decoded_data):
    """
    编码解码后的 block_data，处理负数和特殊编码的方块 ID，恢复为原始数据格式。
    """
    encoded_data = []
    for value in decoded_data:
        if value <= 127:
            # 如果值小于等于 127，直接添加
            encoded_data.append(value)
        else:
            # 需要分割为多个字节，处理超出 127 的数值
            negative_value = (value % 128) - 128  # 计算负数部分
            next_value = value // 128      # 计算增量部分

            # 确保编码后的值在 -128 到 127 范围内
            if negative_value < -128 or negative_value > 127:
                raise ValueError(f"编码值 {negative_value} 超出了 ByteArray 可接受范围")
            if next_value < -128 or next_value > 127:
                raise ValueError(f"增量值 {next_value} 超出了 ByteArray 可接受范围")

            encoded_data.append(negative_value)
            encoded_data.append(next_value)

    return encoded_data

def decode_block_data(block_data):
    """
    解码 block_data，把负数和特殊编码的方块 ID 转换为正确的无符号数或计算值。
    """
    decoded_data = []
    i = 0

    while i < len(block_data):
        value = block_data[i]
        
        if value == 127:
            decoded_data.append(value)  # Start mark as Byte(127)
            i += 1
        elif value < 0:
            negative_value = value
            next_value = block_data[i + 1]
            
            # 根据规则计算最终值
            calculated_value = (next_value + 1) * 128 + negative_value
            decoded_data.append(calculated_value)
            i += 2  # 跳过下一个增量值
        else:
            decoded_data.append(value)  # 正常的 Byte(x)
            i += 1

    return decoded_data

def build_output_data(block_data, palette, width, height, length):
    """
    根据 block_data 和 palette 构建输出数据，包括方块名称和三维坐标。
    """
    # 解码 block_data
    decoded_block_data = decode_block_data(block_data)

    # 构建反向映射
    id_to_block = {v: k for k, v in palette.items()}

    # 构建输出数据
    output_data = []
    index = 0
    for y in range(height):
        for z in range(length):
            for x in range(width):
                if index >= len(decoded_block_data):
                    break
                block_id = decoded_block_data[index]
                block_name = id_to_block.get(block_id, 'unknown')
                output_data.append({
                    'block': block_name,
                    'coordinates': (x, y, z)
                })
                index += 1

    print(f"✅ 成功加载 {len(output_data)} 个方块数据！")
    print(f"✅ 成功加载 {len(palette)} 个方块 ID！")
    print(f"✅ 地图尺寸 (宽度x): {int(width)}，(高度y): {int(height)}，(长度z): {int(length)}")
    
    return output_data

def generate_schem(block_array, palette, width, height, length, filename):
    """
    将方块数组和 palette 转换为 .schem 文件。

    参数：
    block_array: 3D numpy 数组，表示方块在空间中的排布。
    palette: 字典，映射方块名称到方块 ID（如 {'minecraft:air': 0, 'minecraft:gold_block': 1}）。
    width: X 轴方向的长度。
    height: Y 轴方向的长度。
    length: Z 轴方向的长度。
    filename: 输出的 .schem 文件名（如 'output.schem'）。
    """
    
    # 构建 BlockData，确保 Y 轴倒序，这样在 Minecraft 中是“从下往上”展示
    block_data = []
    for y in range(height):
        for z in range(length):
            for x in range(width):
                block_data.append(block_array[y, z, x])

    # 编码 block_data
    encoded_block_data = encode_block_data(block_data)

    # 转换为 ByteArray 格式（编码后的数据不会超出 int8 范围）
    block_data = ByteArray(encoded_block_data)

    # 构建 NBT 数据
    schem_data = File(Compound({
        'Palette': Compound({block: Int(id) for block, id in palette.items()}),
        'PaletteMax': Int(len(palette)),
        'BlockData': block_data,
        'Width': Int(width),
        'Height': Int(height),
        'Length': Int(length),
        'Version': Int(1)
    }))

    # 保存为 .schem 文件
    with open(filename, 'wb') as f:
        schem_data.write(f)

    print(f"✅ 成功生成 '{filename}' 文件！")

def parse_short(value):
    return int(value.split('(')[1].rstrip(')'))

def preview_point_cloud(output_data, air_block='minecraft:air', point_size=50):
    """
    使用 PyVista 可视化 Minecraft 方块数据的点云。
    """
    points = []
    colors = []

    for data in output_data:
        x, y, z = data['coordinates']
        block_name = data['block']

        if block_name == air_block:
            continue  # 跳过空气方块

        # 把坐标加入点云，同时把 y 和 z 对调，让模型“站正”
        points.append([x, z, y])

        # 给不同的方块一个颜色（简单用哈希生成颜色）
        color = hash(block_name) % 0xFFFFFF  # 转成 24 位颜色
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        colors.append([r, g, b])

    # 转换为 NumPy 数组
    points = np.array(points)
    colors = np.array(colors)

    if len(points) == 0:
        print("❌ 没有可视化的方块（可能都是空气方块）")
        return

    # 用 PyVista 创建点云
    cloud = pv.PolyData(points)
    cloud['colors'] = colors / 255.0  # PyVista 需要 0-1 范围的 RGB

    # 绘图
    plotter = pv.Plotter()
    plotter.add_points(cloud, scalars='colors', rgb=True, point_size=point_size)
    plotter.show()

def preview_cubes_with_colors(output_data, air_block='minecraft:air'):
    """
    根据 Minecraft 方块数据生成立方体，并为每个方块设置不同的颜色。
    """
    plotter = pv.Plotter()

    for data in output_data:
        x, y, z = data['coordinates']
        block_name = data['block']

        if block_name == air_block:
            continue  # 跳过空气方块

        # 生成立方体
        cube = pv.Cube(center=(x, z, y), x_length=1, y_length=1, z_length=1)

        # 生成颜色（哈希转颜色）
        color = hash(block_name) % 0xFFFFFF
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        color = [r / 255.0, g / 255.0, b / 255.0]

        # 直接在 add_mesh 里传颜色，避免 point_data 的问题
        plotter.add_mesh(cube, color=color, show_edges=False)

    plotter.show()

def preview_slices(output_data, slice_axis='z', air_block='minecraft:air'):
    """
    使用 PyVista 可视化 Minecraft 方块数据的切片展示。
    """
    slices = []
    blocks = []

    for data in output_data:
        x, y, z = data['coordinates']
        block_name = data['block']

        if block_name == air_block:
            continue  # 跳过空气方块

        # 按切片轴对方块进行分组
        if slice_axis == 'z':
            slices.append(z)
        elif slice_axis == 'y':
            slices.append(y)
        else:
            slices.append(x)

        blocks.append([x, y, z])

    # 获取唯一的切片层（去重）
    slice_layers = list(set(slices))
    slice_layers.sort()

    # 构建并展示每一层切片
    plotter = pv.Plotter()
    for slice_layer in slice_layers:
        slice_data = [block for i, block in enumerate(blocks) if blocks[i][2] == slice_layer]
        points = np.array(slice_data)

        if len(points) > 0:
            cloud = pv.PolyData(points)
            plotter.add_points(cloud, color='blue', point_size=5)

    plotter.show()

def rotate_block(x, y, z, rotation_angle, max_x, max_z):
    if rotation_angle == 90:
        return z, y, max_x - x
    elif rotation_angle == 180:
        return max_x - x, y, max_z - z
    elif rotation_angle == 270:
        return max_z - z, y, x
    return x, y, z

def rotate_attr_vector(block_type, attr_vector, rotation_angle):
    if block_type == BLOCK_TYPE_MAP["stairs"] or block_type == BLOCK_TYPE_MAP["door"]:
        facing = attr_vector[0]
        new_facing = (facing + rotation_angle // 90) % 4
        attr_vector[0] = new_facing
    elif block_type == BLOCK_TYPE_MAP["log"]:
        axis = attr_vector[0]
        axis_map = {0: 2, 2: 0} if rotation_angle in [90, 270] else {0: 0, 1: 1, 2: 2}
        attr_vector[0] = axis_map.get(axis, axis)
    elif block_type in [BLOCK_TYPE_MAP["fence"], BLOCK_TYPE_MAP["glass_pane"]]:
        east, north, south, waterlogged, west = attr_vector
        if rotation_angle == 90:
            attr_vector = [north, west, east, waterlogged, south]
        elif rotation_angle == 180:
            attr_vector = [west, south, north, waterlogged, east]
        elif rotation_angle == 270:
            attr_vector = [south, east, west, waterlogged, north]
    return attr_vector

def mirror_block(x, y, z, mirror_direction, max_x, max_z):
    if mirror_direction == "north_south":
        return max_x - x, y, z
    elif mirror_direction == "east_west":
        return x, y, max_z - z
    return x, y, z

def mirror_attr_vector(block_type, attr_vector, mirror_direction):
    if block_type == BLOCK_TYPE_MAP["stairs"] or block_type == BLOCK_TYPE_MAP["door"]:
        facing = attr_vector[0]
        if mirror_direction == "north_south":
            attr_vector[0] = facing if facing in [0, 2] else 4 - facing
            if block_type == BLOCK_TYPE_MAP["door"]:
                attr_vector[2] = abs(attr_vector[2] - 1)
            elif block_type == BLOCK_TYPE_MAP["stairs"]:
                if attr_vector[2] in {1, 2, 3, 4}:
                    attr_vector[2] = {1: 2, 2: 1, 3: 4, 4: 3}.get(attr_vector[2], attr_vector[2])
        elif mirror_direction == "east_west":
            attr_vector[0] = facing if facing in [1, 3] else 2 - facing
            if block_type == BLOCK_TYPE_MAP["door"]:
                attr_vector[2] = abs(attr_vector[2] - 1)
            elif block_type == BLOCK_TYPE_MAP["stairs"]:
                if attr_vector[2] in {1, 2, 3, 4}:
                    attr_vector[2] = {1: 2, 2: 1, 3: 4, 4: 3}.get(attr_vector[2], attr_vector[2])
    elif block_type in [BLOCK_TYPE_MAP["fence"], BLOCK_TYPE_MAP["glass_pane"]]:
        east, north, south, waterlogged, west = attr_vector            
        if mirror_direction == "north_south":
            attr_vector = [east, south, north, waterlogged, west]
        elif mirror_direction == "east_west":
            attr_vector = [west, north, south, waterlogged, east]
    return attr_vector

def parse_block(block_str):
    match = re.match(r"minecraft:(\w+)(?:\[(.*?)\])?", block_str)
    if not match:
        return None

    block_name, properties = match.groups()
    for key in BLOCK_TYPE_MAP:
        if key in block_name:
            block_type = BLOCK_TYPE_MAP[key]
            break
    else:
        print(f"未知方块类型: {block_name}")
        return None

    attr_vector = []
    subtype = -1
    prop_dict = {}
    if properties:
        prop_dict = dict(prop.split('=') for prop in properties.split(','))

    if block_type == BLOCK_TYPE_MAP["stairs"]:
        subtype = STAIR_SUBTYPE_MAP.get(block_name, -1)
        attr_vector = [
            ["north", "east", "south", "west"].index(prop_dict.get("facing", "north")),
            0 if prop_dict.get("half", "bottom") == "bottom" else 1,
            ["straight","inner_left", "inner_right", "outer_left", "outer_right"].index(prop_dict.get("shape", "straight")),
            0 if prop_dict.get("waterlogged", "false") == "false" else 1
        ]
    elif block_type == BLOCK_TYPE_MAP["log"]:
        axis_map = {'x': 0, 'y': 1, 'z': 2}
        attr_vector = [axis_map.get(prop_dict.get('axis', 'y'))]
    elif block_type == BLOCK_TYPE_MAP["slab"]:
        attr_vector = [
            0 if prop_dict.get("type", "bottom") == "bottom" else 1,
            0 if prop_dict.get("waterlogged", "false") == "false" else 1
        ]
    elif block_type in (BLOCK_TYPE_MAP["fence"], BLOCK_TYPE_MAP["glass_pane"]):
        attr_vector = [
            0 if prop_dict.get("east", "false") == "false" else 1,
            0 if prop_dict.get("north", "false") == "false" else 1,
            0 if prop_dict.get("south", "false") == "false" else 1,
            0 if prop_dict.get("waterlogged", "false") == "false" else 1,
            0 if prop_dict.get("west", "false") == "false" else 1
        ]
    elif block_type == BLOCK_TYPE_MAP["door"]:
        attr_vector = [
            ["north", "east", "south", "west"].index(prop_dict.get("facing", "north")),
            0 if prop_dict.get("half", "lower") == "lower" else 1,
            0 if prop_dict.get("hinge", "left") == "left" else 1,
            0 if prop_dict.get("open", "false") == "false" else 1,
            0 if prop_dict.get("powered", "false") == "false" else 1
        ]
    elif block_type == BLOCK_TYPE_MAP["grass_block"]:
        attr_vector = [0 if prop_dict.get("snowy", "false") == "false" else 1]
    elif block_type == BLOCK_TYPE_MAP["air"]:
        attr_vector = []
    while len(attr_vector) < 5:
        attr_vector.append(-1)
    return (block_type, subtype, attr_vector)

def process_block_data(schem_file):
    # 加载 .schem 文件
    schem_data = load(schem_file)
    palette = schem_data['Palette']
    block_data = schem_data['BlockData']
    width = schem_data['Width']
    height = schem_data['Height']
    length = schem_data['Length']

    # 解码 block_data
    decoded_block_data = decode_block_data(block_data)

    # 构建输出数据
    output_data = build_output_data(decoded_block_data, palette, width, height, length)
    
    # 用户输入检测
    while True:
        user_input = input("请输入要可视化的选项（1: 点云, 2: 切片, 3: 彩色立方体, 13: 点云和彩色立方体, q/Q: 退出）：")
        
        if user_input.lower() in ['q', 'Q']:
            print("退出程序。")
            break
        else:
            # 检查用户输入中是否包含 1、2 或 3
            if '1' in user_input:
                preview_point_cloud(output_data)
            if '2' in user_input:
                preview_slices(output_data)
            if '3' in user_input:
                preview_cubes_with_colors(output_data)
            if '1' not in user_input and '2' not in user_input and '3' not in user_input:
                print("无效的输入，请重新输入。")
                
    # 保存方块数据到文本文件
    with open('block_data.txt', 'w', encoding='utf-8') as f:
        for block in output_data:
            x, y, z = block['coordinates']
            block_name = block['block']
            if block_name == 'minecraft:dirt':
                block_name = 'minecraft:grass_block[snowy=false]'
            if x == 9 and y == 9 and z == 9:
                block_name = 'minecraft:air'
            elif x == 0 and y == 9 and z == 9:
                block_name = 'minecraft:air'
            elif x == 0 and y == 9 and z == 0:
                block_name = 'minecraft:air'
            elif x == 9 and y == 9 and z == 0:
                block_name = 'minecraft:air'
            f.write(f"{x},{y},{z},{block_name}\n")

    # 保存元数据
    with open('metadata.txt', 'w', encoding='utf-8') as f:
        f.write(f"{width},{height},{length}\n")
        for block, block_id in palette.items():
            f.write(f"{block},{block_id}\n")
    print("✅ 方块数据已成功导出到 block_data.txt！")
    print("✅ 元数据已成功导出到 metadata.txt！")

def parse_and_process_block_data():
    input_file = "block_data.txt"
    output_file = "parsed_block_data.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        block_data = f.readlines()

    with open(output_file, "w", encoding="utf-8") as f:
        for line in block_data:
            parts = line.strip().split(',', 3)
            x, y, z, block_name = parts
            result = int(x), int(y), int(z), parse_block(block_name)
            if result:
                f.write(f"{result}\n")
    print(f"✅ 解析完成，结果已保存到 {output_file}")

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

def generate_rotated_and_mirrored_data():
    input_file = "parsed_block_data.txt"
    output_file = "block_data_"

    blocks_original, blocks_90, blocks_180, blocks_270, blocks_mirror_north_south, blocks_mirror_east_west = [], [], [], [], [], []

    with open('metadata.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        width, height, length = map(parse_short, lines[0].strip().split(','))

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = eval(line)
            x, y, z, (block_type, subtype, attr_vector) = parts

            blocks_original.append([x, y, z, block_type, subtype] + attr_vector)

            for angle in [90, 180, 270]:
                new_x, new_y, new_z = rotate_block(x, y, z, angle, width-1, length-1)
                new_attr_vector = rotate_attr_vector(block_type, attr_vector.copy(), angle)
                locals()[f"blocks_{angle}"].append([new_x, new_y, new_z, block_type, subtype] + new_attr_vector)

            for direction in ["north_south", "east_west"]:
                new_x, new_y, new_z = mirror_block(x, y, z, direction, width-1, length-1)
                new_attr_vector = mirror_attr_vector(block_type, attr_vector.copy(), direction)
                locals()[f"blocks_mirror_{direction}"].append([new_x, new_y, new_z, block_type, subtype] + new_attr_vector)

    arrays = [blocks_original, blocks_90, blocks_180, blocks_270, blocks_mirror_north_south, blocks_mirror_east_west]
    for i in range(len(arrays)):
        arrays[i] = sorted(arrays[i], key=lambda block: (block[0], block[1], block[2]))

    original_array = np.array(blocks_original, dtype=np.int32)
    mirror_north_south_array = np.array(blocks_mirror_north_south, dtype=np.int32)
    mirror_east_west_array = np.array(blocks_mirror_east_west, dtype=np.int32)

    original_array = original_array[np.lexsort(original_array[:, :3].T)]
    mirror_north_south_array = mirror_north_south_array[np.lexsort(mirror_north_south_array[:, :3].T)]
    mirror_east_west_array = mirror_east_west_array[np.lexsort(mirror_east_west_array[:, :3].T)]

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

        np.save(output_file + str(i), structure)
        print(f"✅ 数据成功保存到 {output_file + str(i)}.npy，形状为 {structure.shape}")

def compare_npy_and_txt(npy_file, input_txt, check_file):
    """
    比较 .npy 文件和解析后的文本文件，检查两者是否一致。

    参数：
    npy_file: .npy 文件路径。
    input_txt: 解析后的文本文件路径。
    check_file: 保存比对结果的文本文件路径。
    """
    # 加载 .npy 数据
    structure = np.load(npy_file)

    # 获取形状信息
    W, H, D, _ = structure.shape

    # 把 npy 文件还原为文本格式
    reconstructed_lines = []

    # 修正遍历顺序，确保是 (x, y, z)
    for y in range(H):
        for z in range(D):
            for x in range(W):
                block_data = structure[x, y, z]

                # 不跳过 -1，保留检查完整性
                block_type, subtype, *attr_vector = block_data
                block_type = int(block_type)
                subtype = int(subtype)
                attr_vector = [int(v) for v in attr_vector]

                # 还原成文本行格式
                reconstructed_line = f"({x}, {y}, {z}, ({block_type}, {subtype}, {attr_vector}))"
                reconstructed_lines.append(reconstructed_line)

    # 读取原始文本数据
    with open(input_txt, "r", encoding="utf-8") as f:
        original_lines = [line.strip() for line in f.readlines()]

    # 比对并写入检查文件
    with open(check_file, "w", encoding="utf-8") as f:
        max_len = max(len(original_lines), len(reconstructed_lines))

        for i in range(max_len):
            orig = original_lines[i] if i < len(original_lines) else "[原文件缺失行]"
            recon = reconstructed_lines[i] if i < len(reconstructed_lines) else "[还原文件缺失行]"

            if orig != recon:
                f.write(f"❌ 差异行:\n原始:   {orig}\n还原:   {recon}\n\n")
            else:
                f.write(f"✅ 一致行:\n{orig}\n\n")

    print(f"检查完成，结果保存到 {check_file}")

def check_accuracy_of_txt2npy():
    # 比较生成的 .npy 文件和解析后的文本文件
    npy_file = "block_data_0.npy"  # 替换为你的 .npy 文件路径
    input_txt = "parsed_block_data.txt"  # 替换为你的解析后的文本文件路径
    check_file = "check_txt2npy.txt"  # 替换为你的检查结果文件路径
    compare_npy_and_txt(npy_file, input_txt, check_file)
    
def main():
    schem_file = "WoodHouse_3.schem"  # 替换为你的 .schem 文件路径
    process_block_data(schem_file)
    parse_and_process_block_data()
    generate_rotated_and_mirrored_data()
    
    # 是否需要检查生成的 .npy 与 .txt 文件的一致性
    check_accuracy_of_txt2npy()


if __name__ == "__main__":
    main()


from flask import Flask, request, session, render_template
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置安全密钥

# 加载翻译文件
def load_translations(lang='en'):
    with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 设置默认语言
@app.before_request
def set_default_language():
    if 'lang' not in session:
        session['lang'] = 'en'  # 默认英文

# 语言切换路由
@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    return redirect_back()  # 返回上一页

# 渲染模板时注入翻译
@app.route('/')
def index():
    translations = load_translations(session['lang'])
    return render_template('index.html', _=translations)