# Windows EXE 打包指南

本指南将帮助您在Windows系统上将ChatGLM视频生成工具打包成EXE可执行文件。

## 前提条件

1. **Windows 10/11** 系统
2. **Python 3.8+** 已安装
3. **Git** (可选，用于克隆代码)

## 步骤1: 准备环境

### 1.1 下载项目
```powershell
# 方式1: 使用Git克隆
git clone <your-repo-url>
cd rpa-glm

# 方式2: 直接下载ZIP文件并解压到文件夹
```

### 1.2 创建虚拟环境
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 验证虚拟环境
where python
# 应该显示虚拟环境中的python路径
```

### 1.3 安装依赖
```powershell
# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖（使用预编译包避免编译问题）
pip install --only-binary=all pandas openpyxl
pip install -r requirements.txt
```

### 1.4 检查环境
```powershell
# 测试是否能正常导入主要模块
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 导入成功')"
python -c "import playwright; print('Playwright 导入成功')"
python -c "import pandas; print('Pandas 导入成功')"

# 如果都没有报错，说明环境正常
```

## 步骤2: 测试程序

```powershell
# 测试GUI程序是否正常运行
python main.py

# 确保程序能正常启动和显示界面
```

## 步骤3: 执行打包

### 3.1 使用spec文件打包（推荐）
```powershell
# 使用预配置的spec文件
python -m PyInstaller chatglm_video_tool.spec
```

**如果出现"pyinstaller不是内部或外部命令"错误：**
```powershell
# 检查PyInstaller是否安装
python -c "import PyInstaller; print('PyInstaller已安装:', PyInstaller.__version__)"

# 使用python模块方式运行（100%有效）
python -m PyInstaller --version
python -m PyInstaller chatglm_video_tool.spec
```

### 3.2 或使用命令行打包（单文件）
```powershell
# 一条命令打包成单一EXE文件
pyinstaller --onefile --windowed --name "ChatGLM视频生成工具" ^
    --add-data "config;config" ^
    --add-data "src;src" ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import yaml ^
    --hidden-import asyncio ^
    main.py
```

**注意**: 
- `--onefile` 参数确保生成单一EXE文件
- 所有YAML配置文件和源代码都会被打包到EXE内部
- 最终只生成一个独立的EXE文件，无需任何附加文件

## 步骤4: 测试EXE文件

```powershell
# 进入输出目录
cd dist

# 运行生成的EXE文件
.\ChatGLM视频生成工具.exe

# 测试基本功能:
# 1. 界面是否正常显示
# 2. 配置是否能正常设置
# 3. 日志是否正常显示
```

## 步骤5: 单文件EXE优势

使用我们的配置，您将得到：
- **单一EXE文件**：所有依赖、配置、源代码都在一个文件中
- **无需附加文件**：不需要YAML、JSON或任何其他文件
- **完全独立运行**：可以直接分发给用户，双击即可使用

```powershell
# 打包完成后，只需要这一个文件
.\ChatGLM视频生成工具.exe
```

## 步骤6: 创建发布包（可选）

如果需要包含说明文档：

```powershell
# 创建发布目录
mkdir ChatGLM视频生成工具_v1.0
cd ChatGLM视频生成工具_v1.0

# 复制EXE文件（这是唯一必需的文件）
copy ..\dist\ChatGLM视频生成工具.exe .

# 可选：复制说明文档
copy ..\README.md .
```

## 故障排除

### 常见问题1: 依赖安装失败（编译错误）
```
错误信息: Microsoft Visual C++ 14.0 or greater is required
错误信息: Unknown compiler(s): [['cl'], ['gcc'], ...]

解决方案:
1. 强制使用预编译包: pip install --only-binary=all pandas openpyxl
2. 清理冲突依赖: pip uninstall pandas numpy greenlet -y
3. 使用python模块方式: python -m pip install --upgrade pip
4. 分步安装: pip install PyQt6 playwright requests loguru PyYAML PyInstaller
```

### 常见问题2: 打包失败
```
解决方案:
1. 确保虚拟环境已激活
2. 重新安装依赖: pip install -r requirements.txt
3. 更新PyInstaller: pip install --upgrade PyInstaller
```

### 常见问题3: EXE文件太大
```
解决方案:
1. 在spec文件中排除不需要的模块
2. 使用 --exclude-module 参数排除大型库
```

### 常见问题4: EXE运行时缺少模块
```
解决方案:
1. 在spec文件的hiddenimports中添加缺失的模块
2. 使用 --hidden-import 参数添加隐藏导入
```

### 常见问题5: 中文路径问题
```
解决方案:
1. 确保项目路径不包含中文字符
2. 使用英文路径进行打包
```

## 高级配置

### 自定义图标
```powershell
# 如果有图标文件(icon.ico)
pyinstaller --icon=icon.ico chatglm_video_tool.spec
```

### 添加版本信息
版本信息已在 `version_info.txt` 中配置，包含:
- 程序名称
- 版本号
- 描述信息
- 公司信息

### 优化文件大小
在spec文件中可以排除不需要的模块:
```python
excludes=[
    'matplotlib',
    'scipy', 
    'numpy',
    'PIL',
    'tkinter',
]
```

## 最终检查清单

- [ ] 虚拟环境已激活
- [ ] 所有依赖已安装
- [ ] 主要模块导入测试通过
- [ ] GUI程序可以正常运行
- [ ] EXE文件生成成功
- [ ] EXE文件可以正常运行
- [ ] 界面显示正常
- [ ] 日志功能正常
- [ ] 配置保存/加载正常

## 单文件打包技术说明

我们的配置实现了真正的单文件打包：

1. **所有配置文件内嵌**：`config/web_elements.yaml` 被打包到EXE内部
2. **源代码内嵌**：整个 `src/` 目录被打包到EXE内部  
3. **依赖库内嵌**：PyQt6、Playwright等所有依赖都在EXE内
4. **运行时自动解压**：EXE运行时会自动解压到临时目录
5. **无外部依赖**：目标机器无需安装Python或任何依赖

## 注意事项

1. **首次打包可能较慢**，PyInstaller需要分析所有依赖
2. **EXE文件较大**是正常的（约50-100MB），因为包含了完整的Python运行环境
3. **杀毒软件**可能会误报，这是PyInstaller的常见问题
4. **路径问题**：确保不要在包含中文的路径下打包
5. **权限问题**：某些系统可能需要管理员权限运行
6. **首次运行稍慢**：单文件EXE首次运行时需要解压，后续运行会快很多

## 分发说明

生成的EXE文件是独立的，可以在其他Windows机器上运行，无需安装Python环境。

用户只需要:
1. 下载EXE文件
2. 双击运行
3. 按照GUI界面提示配置使用

---

如有问题，请检查本指南的故障排除部分或查看项目文档。 