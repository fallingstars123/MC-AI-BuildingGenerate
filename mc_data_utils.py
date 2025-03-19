import numpy as np
import pyvista as pv
from nbtlib import File, Compound, Int, ByteArray

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
    # print(block_data[37776])
    # 编码 block_data
    encoded_block_data = encode_block_data(block_data)
    # print(encoded_block_data[37776])
    # print(encoded_block_data[37777])

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
        # cube = pv.Cube(center=(x, z, y), x_length=0.8, y_length=0.8, z_length=0.8)
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

    """
    使用 PyVista 可视化建筑的等值面。
    """
    points = []
    values = []

    for data in output_data:
        x, y, z = data['coordinates']
        block_name = data['block']

        if block_name == air_block:
            continue  # 跳过空气方块

        # 按照某些特征给每个方块一个值，例如根据方块 ID 或类型
        value = hash(block_name) % 1000  # 示例: 用方块哈希值作为值

        points.append([x, z, y])
        values.append(value)

    if len(points) == 0:
        print("❌ 没有可视化的方块（可能都是空气方块）")
        return

    # 创建点云并进行等值面提取
    points = np.array(points)
    values = np.array(values)
    cloud = pv.PolyData(points)
    cloud.point_data['values'] = values

    # 提取等值面
    iso = cloud.contour([threshold])  # 提取等值面
    iso.plot()
