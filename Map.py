import re

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
#门的依附侧要改改
STAIR_SUBTYPE_MAP = {
    "oak_stairs": 0,
    "dark_oak_stairs": 1,
    "birch_stairs": 2,
    "spruce_stairs": 3
}

def rotate_block(x, y, z, rotation_angle, max_x, max_z):
    """根据旋转角度和最大坐标范围旋转方块的坐标。"""
    if rotation_angle == 90:
        return z, y, max_x - x
    elif rotation_angle == 180:
        return max_x - x, y, max_z - z
    elif rotation_angle == 270:
        return max_z - z, y, x
    return x, y, z

def rotate_attr_vector(block_type, attr_vector, rotation_angle):
    """根据旋转角度调整方块的属性向量。"""
    if block_type == BLOCK_TYPE_MAP["stairs"] or block_type == BLOCK_TYPE_MAP["door"]:
        # 旋转朝向（0: 北, 1: 东, 2: 南, 3: 西）
        facing = attr_vector[0]
        new_facing = (facing + rotation_angle // 90) % 4
        attr_vector[0] = new_facing
    elif block_type == BLOCK_TYPE_MAP["log"]:
        # 旋转木头轴向（0: x, 1: y, 2: z）
        axis = attr_vector[0]
        axis_map = {0: 2, 2: 0} if rotation_angle in [90, 270] else {0: 0, 1: 1, 2: 2}
        attr_vector[0] = axis_map.get(axis, axis)
    elif block_type in [BLOCK_TYPE_MAP["fence"], BLOCK_TYPE_MAP["glass_pane"]]:
        # attr_vector 顺序为 [east, north, south, waterlogged, west]
        east, north, south, waterlogged, west = attr_vector
        if rotation_angle == 90:
            attr_vector = [north, west, east, waterlogged, south]
        elif rotation_angle == 180:
            attr_vector = [west, south, north, waterlogged, east]
        elif rotation_angle == 270:
            attr_vector = [south, east, west, waterlogged, north]
    return attr_vector

def mirror_block(x, y, z, mirror_direction, max_x, max_z):
    """根据镜像方向和最大坐标范围调整方块的坐标。"""
    if mirror_direction == "north_south":
        return max_x - x, y, z
    elif mirror_direction == "east_west":
        return x, y, max_z - z
    return x, y, z

def mirror_attr_vector(block_type, attr_vector, mirror_direction):
    """根据镜像方向调整方块的属性向量。"""
    if block_type == BLOCK_TYPE_MAP["stairs"] or block_type == BLOCK_TYPE_MAP["door"]:
        facing = attr_vector[0]
        if mirror_direction == "north_south":
            # 北南镜像翻转南北方向
            attr_vector[0] = facing if facing in [0, 2] else 4 - facing
            if block_type == BLOCK_TYPE_MAP["door"]:
                # 门需要额外调整
                attr_vector[2] = abs(attr_vector[2] - 1)
            elif block_type == BLOCK_TYPE_MAP["stairs"]:
                # 楼梯需要额外调整
                # staight = 0, inner_left = 1, inner_right = 2, outer_left = 3, outer_right = 4
                if attr_vector[2] in {1, 2, 3, 4}:
                    attr_vector[2] = {1: 2, 2: 1, 3: 4, 4: 3}.get(attr_vector[2], attr_vector[2])
        elif mirror_direction == "east_west":
            # 东西镜像翻转东西方向
            attr_vector[0] = facing if facing in [1, 3] else 2 - facing
            if block_type == BLOCK_TYPE_MAP["door"]:
                # 门需要额外调整
                attr_vector[2] = abs(attr_vector[2] - 1)
            elif block_type == BLOCK_TYPE_MAP["stairs"]:
                # 楼梯需要额外调整
                # staight = 0, inner_left = 1, inner_right = 2, outer_left = 3, outer_right = 4
                if attr_vector[2] in {1, 2, 3, 4}:
                    attr_vector[2] = {1: 2, 2: 1, 3: 4, 4: 3}.get(attr_vector[2], attr_vector[2])
    elif block_type in [BLOCK_TYPE_MAP["fence"], BLOCK_TYPE_MAP["glass_pane"]]:
        # attr_vector 顺序为 [east, north, south, waterlogged, west]
        east, north, south, waterlogged, west = attr_vector            
        if mirror_direction == "north_south":
            attr_vector = [east, south, north, waterlogged, west]
        elif mirror_direction == "east_west":
            attr_vector = [west, north, south, waterlogged, east]
    return attr_vector


def parse_block(block_str):
    """
    将方块数据字符串解析为类型编码和属性向量。
    """
    match = re.match(r"minecraft:(\w+)(?:\[(.*?)\])?", block_str)
    if not match:
        return None

    block_name, properties = match.groups()

    # 提取方块类型（忽略前缀，如 oak_stairs、dark_oak_stairs 都归为 stairs）
    for key in BLOCK_TYPE_MAP:
        if key in block_name:
            block_type = BLOCK_TYPE_MAP[key]
            break
    else:
        print(f"未知方块类型: {block_name}")
        return None

    # 初始化属性向量和子类型
    attr_vector = []
    subtype = -1

    # 解析属性字典
    prop_dict = {}
    if properties:
        prop_dict = dict(prop.split('=') for prop in properties.split(','))

    # 确定子类型
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
# 读取并解析 block_data.txt
input_file = "block_data.txt"
output_file = "parsed_block_data.txt"

with open(input_file, "r", encoding="utf-8") as f:
    block_data = f.readlines()

with open(output_file, "w", encoding="utf-8") as f:
    for line in block_data:
        parts = line.strip().split(',', 3)  # 从左边最多分割三次，确保前三个是坐标，剩下的是方块名称
        x, y, z, block_name = parts
        result = int(x), int(y), int(z), parse_block(block_name)
        if result:
            f.write(f"{result}\n")

print(f"解析完成，结果已保存到 {output_file}")
