# 智能MC建筑生成器

## 项目介绍  
智能MC建筑生成器是一个基于人工智能的工具，能够根据用户输入的提示词（如“平顶”、“深色橡木墙”）自动生成《我的世界》（Minecraft）中的建筑。项目结合了数据增强、3D生成模型和Minecraft数据格式转换技术，支持从单张图像或文本提示词生成10x10x10大小的建筑，并导出为 `.schem` 文件。
---
[🇨🇳 简体中文](README.zh.md) | [🇬🇧 English](README.en.md)
---

## 主要功能  
1. **数据加载与解析**：支持加载 `.schem` 文件，解析其中的方块数据。  
2. **数据增强**：通过旋转和镜像操作，生成多样化的建筑变体。  
3. **可视化**：支持点云、切片和彩色立方体等多种方式预览建筑。  
4. **提示词生成**：根据用户输入的提示词生成建筑。  
5. **导出功能**：将生成的建筑保存为 `.schem` 文件，供Minecraft使用。  

---

## 依赖项  
• **Python 3.8+**  
• **主要库**：  
  • `numpy`  
  • `pyvista`  
  • `nbtlib`  
  • `torch`（用于模型训练）  
  • `flask`（用于Web界面）  

**安装依赖项**：  
```
pip install numpy pyvista nbtlib torch flask
```

---

## 使用方法  

### 1. 数据加载与解析  
将 `.schem` 文件放入项目目录，运行以下代码加载和解析数据：  
```python
from main import process_block_data  
process_block_data("WoodHouse_3.schem")  
```

### 2. 数据增强  
对现有建筑数据进行旋转和镜像增强：  
```python
from main import generate_rotated_and_mirrored_data  
generate_rotated_and_mirrored_data()  
```

### 3. 可视化  
使用以下命令预览建筑：  
```python
from main import preview_point_cloud, preview_cubes_with_colors, preview_slices  
preview_point_cloud(output_data)  # 点云预览  
preview_cubes_with_colors(output_data)  # 彩色立方体预览  
preview_slices(output_data)  # 切片预览  
```

### 4. 提示词生成  
根据提示词生成建筑：  
```python
from main import generate_from_prompt  
generate_from_prompt("A small house with a flat roof and dark oak walls")  
```

### 5. 导出为 `.schem` 文件  
将生成的建筑保存为 `.schem` 文件：  
```python
from main import save_as_schem  
save_as_schem(house_data, "generated_house.schem")  
```

### 6. Web界面  
启动Web服务器，提供用户交互界面：  
```
python main.py  
```  
访问 `http://Not_created_yet`，输入提示词生成建筑。  

---

## 文件结构  
```
MC_Building_Generator/  
├── main.py                  # 主程序  
├── block_data.txt           # 解析后的方块数据  
├── metadata.txt             # 元数据  
├── block_data_0.npy         # 增强后的建筑数据  
├── generated_house.schem    # 生成的建筑文件  
├── README.md                # 项目说明  
```

---

## 示例  
1. **加载 `.schem` 文件**：  
   ```bash
   python main.py  
   ```  
2. **输入提示词生成建筑**：  
   • **提示词**：`A small house with a flat roof and dark oak walls`  
   • **生成文件**：`generated_house.schem`  

---

## 注意事项  
1. 确保 `.schem` 文件符合Minecraft的格式要求。  
2. 提示词应尽量简洁明确，避免歧义。  
3. 生成的建筑数据会保存在 `block_data_*.npy` 文件中。  

---

## 未来计划  
1. 支持更多建筑类型和尺寸。  
2. 优化生成模型，提高生成速度和精度。  
3. 开发更友好的用户界面，支持实时预览。  

---

## 联系信息  
如有任何问题或建议，请联系：  
• **邮箱**：3467025700@qq.com  
• **GitHub**：[https://github.com/fallingstars123/MC-AI-BuildingGenerate](https://github.com/fallingstars123/MC-AI-BuildingGenerate)  
• **Discord**: thomasw2004
---
