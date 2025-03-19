import numpy as np

input_txt = "parsed_block_data.txt"
npy_file = "block_data_0.npy"
check_file = "check_txt2npy.txt"

# 加载 .npy 数据
structure = np.load(npy_file)

# 获取形状信息
W, H, D, _ = structure.shape

# 把 npy 文件还原为文本格式
reconstructed_lines = []

# 修正遍历顺序，确保是 (x, y, z)
# 尝试调整维度顺序
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
