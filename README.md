# 零基础小白一键用：ChatGLM视频自动生成工具

## 你能用它做什么？

- 批量上传图片+提示词，自动生成视频，自动下载保存
- 全程自动化，无需手动点网页
- 支持多任务批量处理，自动记录进度
- **图形化界面(GUI)，完全通过界面配置，无需编辑文件！**

---

## 1. 环境准备（只需一次）

### 1.1 安装 Python

- 本工具需要 Python 3.8 及以上版本
- Mac 用户自带 Python，但建议用 [官网](https://www.python.org/downloads/) 或 [Anaconda](https://www.anaconda.com/) 安装最新版

### 1.2 安装依赖

打开终端（Terminal），输入：

```bash
pip install -r requirements.txt
```

---

## 2. 一键启动

直接运行：

```bash
python main.py
```

就这么简单！程序会自动打开图形界面。

---

## 3. 界面功能

### 3.1 界面选项卡

- **基本配置选项卡**：设置任务目录、比特浏览器ID、Excel配置等
- **高级配置选项卡**：设置视频质量、延时参数、下载配置等
- **日志输出选项卡**：实时查看程序运行日志

### 3.2 使用步骤

1. 打开GUI界面
2. 在"基本配置"中设置任务根目录和比特浏览器窗口ID
3. 调整其他参数（可选）
4. 点击"开始生成视频"（无需手动保存配置）

### 3.3 配置管理

- **重置为默认配置**：一键恢复默认设置
- **保存为预设**：将当前配置保存为文件，便于分享或备份
- **加载预设**：从文件加载之前保存的配置

---

## 4. 配置说明

### 4.1 任务目录结构

- 在根目录下，每个任务建一个文件夹
- 每个任务文件夹里放：
  - 多张图片，命名为 `1_图片描述.jpg`、`2_图片描述.jpg` ...
  - 一个 Excel 文件（如 `任务列表.xlsx`），**第1行为表头，第2行开始为任务内容**，第3列是图生视频提示词

**示例结构：**
```
视频任务/
├── 老虎救小豹/
│   ├── 1_老虎.jpg
│   ├── 2_小豹.jpg
│   └── 任务列表.xlsx
├── 其它任务/
│   └── ...
```

**Excel 示例：**
| 序号 | 提示词           | 状态         |
|------|------------------|--------------|
| 1    | 老虎救小豹       |              |
| 2    | 小豹跳河         |              |

### 4.2 GUI配置说明

**基本配置**：
- **任务根目录**：存放所有任务文件夹的根目录
- **比特浏览器窗口ID**：在比特浏览器后台找到的窗口ID
- **超时设置**：避免程序等待过久
- **Excel配置**：提示词和状态列的位置设置

**高级配置**：
- **视频质量选项**：画质、帧率、分辨率
- **智能延时**：避免操作过快被网站限制
- **下载配置**：视频下载超时时间

---

## 5. 常见问题与小白答疑

### Q1：GUI界面打不开？
- 确保安装了PyQt6：`pip install PyQt6`
- 检查Python版本是否为3.8+
- 测试模块导入：`python -c "from PyQt6.QtWidgets import QApplication; print('GUI模块正常')"`

### Q2：pip 报错/没权限？
- 用 `python3 -m pip install ...` 或加 `--user` 试试

### Q3：Excel 格式不对怎么办？
- 用 WPS/Excel 新建，第一行是表头，第二行开始是内容，第三列是提示词

### Q4：图片/视频没生成？
- 检查GUI日志选项卡里的日志，按提示排查
- 检查网络、账号额度、图片命名、Excel内容

### Q5：比特浏览器窗口ID怎么查？
- 打开比特浏览器后台，窗口管理里能看到每个窗口的ID，复制粘贴到GUI配置即可

### Q6：配置会保存吗？
- **会自动保存！** 程序每5秒自动保存当前配置
- 下次启动程序时，会自动加载上次的所有设置
- 也可手动使用"保存为预设"功能备份配置

### Q7：可以分享配置吗？
- 可以！使用"保存为预设"将配置保存为JSON或YAML文件
- 将文件发给其他人，他们可以用"加载预设"导入配置

---

## 6. 其它说明

- **所有配置都通过GUI界面完成，无需编辑任何文件**
- **程序会自动保存配置，每次启动都会加载上次的设置**
- **支持配置预设的保存和分享（JSON/YAML格式）**
- **GUI提供实时日志输出，方便排查问题**
- **遇到问题先看GUI日志选项卡，再来问开发者**

---

## 7. 一句话总结

**就是这么简单！运行 `python main.py`，填写配置，一键开始，比用微信还简单！**

---

如需更详细的帮助，欢迎随时提问！ 