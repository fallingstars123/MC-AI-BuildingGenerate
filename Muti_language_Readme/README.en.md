---

# Smart MC Building Generator

## Project Overview  
The Smart MC Building Generator is an AI-powered tool that automatically generates Minecraft structures based on user prompts (e.g., "flat roof", "dark oak walls"). It combines data augmentation, 3D generative models, and Minecraft data format conversion to create 10x10x10 structures from single images or text prompts, exporting them as `.schem` files.
---
[🇨🇳 简体中文](./README.zh.md) | [🇬🇧 English](./README.en.md)
---

## Key Features  
1. **Data Loading & Parsing**  
   • Supports loading and parsing Minecraft `.schem` files.  
2. **Data Augmentation**  
   • Generates diverse building variants via rotation and mirroring.  
3. **3D Visualization**  
   • Preview structures as point clouds, colored cubes, or slice views.  
4. **Prompt-Driven Generation**  
   • Generate buildings from text prompts (e.g., "small house with a flat roof").  
5. **Export Functionality**  
   • Save generated structures as `.schem` files for direct use in Minecraft.  

---

## Dependencies  
• **Python 3.8+**  
• **Core Libraries**:  
  • `numpy`  
  • `pyvista`  
  • `nbtlib`  
  • `torch` (for model training)  
  • `flask` (for web interface)  

**Installation**:  
```bash
pip install numpy pyvista nbtlib torch flask
```

---

## Usage  

### 1. Load & Parse Data  
Place your `.schem` file in the project directory and run:  
```python
from main import process_block_data  
process_block_data("WoodHouse_3.schem")  
```

### 2. Data Augmentation  
Generate rotated/mirrored variants of existing structures:  
```python
from main import generate_rotated_and_mirrored_data  
generate_rotated_and_mirrored_data()  
```

### 3. Visualization  
Preview structures using:  
```python
from main import preview_point_cloud, preview_cubes_with_colors, preview_slices  
preview_point_cloud(output_data)    # Point cloud view  
preview_cubes_with_colors(output_data)  # Colored cubes  
preview_slices(output_data)        # Slice view  
```

### 4. Prompt-Based Generation  
Generate structures from text prompts:  
```python
from main import generate_from_prompt  
generate_from_prompt("A small house with a flat roof and dark oak walls")  
```

### 5. Export to `.schem`  
Save generated structures:  
```python
from main import save_as_schem  
save_as_schem(house_data, "generated_house.schem")  
```

### 6. Web Interface  
Launch the interactive web server:  
```bash
python main.py  
```  
Visit `http://Not_created_yet` to generate buildings via prompts.  

---

## File Structure  
   ```
   MC_Building_Generator/
   ├── schem/                 # put .schem files
   │   └── WoodHouse_3.schem
   ├── npy/                   # put .npy files
   │   └── block_data_0.npy
   ├── main.py                # Main entry point  
   ├── block_data.txt         # Parsed block data  
   ├── metadata.txt           # Metadata (dimensions, block IDs)  
   └── README.md              # This document
   ```
---

## Examples  
1. **Load a `.schem` file**:  
   ```bash
   python main.py  
   ```  
2. **Generate from a prompt**:  
   • **Prompt**: `A small house with a flat roof and dark oak walls`  
   • **Output**: `generated_house.schem`  

---

## Notes  
1. Ensure `.schem` files follow Minecraft's format specifications.  
2. Use clear and specific prompts for optimal results.  
3. Augmented data is saved in `block_data_*.npy` files.  

---

## Roadmap  
1. Support more building types and sizes.  
2. Optimize generation speed and model accuracy.  
3. Develop a real-time preview interface.  

---

## Contact  
For questions or feedback:  
• **Email**: 3467025700@qq.com 
• **GitHub**: [https://github.com/fallingstars123/MC-AI-BuildingGenerate](https://github.com/fallingstars123/MC-AI-BuildingGenerate)  
• **Discord**: thomasw2004

---
