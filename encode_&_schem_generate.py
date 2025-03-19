import numpy as np
from mc_data_utils import generate_schem, encode_block_data, parse_short

# 从 metadata.txt 中读取宽、高、长和 palette
with open('metadata.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

    width, height, length = map(parse_short, lines[0].strip().split(','))
    print(width, height, length)

    palette = {}
    for line in lines[1:]:
        parts = line.strip().rsplit(',', 1)
        if len(parts) != 2:
            print(f"❌ 无法解析行: {line}")
            continue
        block_name, block_id = parts
        block_id = int(block_id.split('(')[1].rstrip(')'))
        palette[block_name] = block_id

# 从 block_data.txt 中读取方块数据并转换为方块 ID
decoded_block_data = []
with open('block_data.txt', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            parts = line.strip().split(',', 3)  # 从左边最多分割三次，确保前三个是坐标，剩下的是方块名称
            x, y, z, block_name = parts
            block_id = palette.get(block_name, 0)  # 默认用空气块填补未知方块
            decoded_block_data.append(block_id)
        except ValueError:
            print(f"❌ 无法解析行: {line}")

# 编码 block_data
encoded_block_data = encode_block_data(decoded_block_data)

# 构建 block_array（3D 方块数组）
block_array = np.zeros((height, length, width), dtype=int)

index = 0
for y in range(height):
    for z in range(length):
        for x in range(width):
            if index < len(decoded_block_data):
                block_array[y, z, x] = decoded_block_data[index]
                index += 1

# 生成 .schem 文件
# filename = 'Test_display.schem'
filename = 'WoodHouse_3.schem'
generate_schem(block_array, palette, width, height, length, filename)

print(f"✅ 成功生成 '{filename}' 文件！")
