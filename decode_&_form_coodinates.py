from nbtlib import load
from mc_data_utils import build_output_data, preview_point_cloud, decode_block_data, preview_cubes_with_colors, preview_slices

# 加载 .schem 文件
# schem_data = load('Ach1.schem')
# schem_data = load('Test_display.schem')
schem_data = load('WoodHouse_3.schem')
# schem_data = load('items.schem')
# schem_data = load('Test_stairs.schem')


# 获取基本数据
palette = schem_data['Palette']
block_data = schem_data['BlockData']
width = schem_data['Width']
height = schem_data['Height']
length = schem_data['Length']

# 解码 block_data
decoded_block_data = decode_block_data(block_data)

# 构建输出数据
output_data = build_output_data(decoded_block_data, palette, width, height, length)

# 把方块数据保存到文本文件
with open('block_data.txt', 'w', encoding='utf-8') as f:
    for block in output_data:
        x, y, z = block['coordinates']
        block_name = block['block']
        # 根据方块名称进行替换
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

# 把元数据保存
with open('metadata.txt', 'w', encoding='utf-8') as f:
    f.write(f"{width},{height},{length}\n")
    for block, block_id in palette.items():
        f.write(f"{block},{block_id}\n")
with open('Print_BD.txt', 'w', encoding='utf-8') as f:
    f.write(f"{block_data}\n")
    # for block, block_id in palette.items():
    #     f.write(f"{block},{block_id}\n")
print("✅ 方块数据已成功导出到 block_data.txt！")
print("✅ 元数据已成功导出到 metadata.txt！")

# 可视化方块点云
preview_point_cloud(output_data)
# preview_slices(output_data)

# 调用函数
# preview_cubes_with_colors(output_data)