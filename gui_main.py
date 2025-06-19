"""
视频生成自动化GUI界面
使用PyQt6实现的图形化用户界面
"""

import sys
import os
import asyncio
import yaml
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QGroupBox, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTextEdit, QProgressBar, QFileDialog,
    QTabWidget, QFormLayout, QGridLayout, QScrollArea, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from loguru import logger
from src.config_manager import config_manager
from src.task_processor import task_processor
from src.logger_handler import gui_log_handler, setup_gui_logging


class TaskWorker(QThread):
    """任务执行线程"""
    progress_updated = pyqtSignal(str)  # 进度更新信号
    task_completed = pyqtSignal(bool)   # 任务完成信号
    
    def __init__(self, config_data):
        super().__init__()
        self.config_data = config_data
        
    def run(self):
        """在后台线程中运行任务"""
        try:
            # 直接将配置传递给config_manager
            config_manager.set_user_config(self.config_data)
            
            # 运行异步任务
            asyncio.run(self.run_task())
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            self.task_completed.emit(False)
    
    async def run_task(self):
        """运行主任务"""
        try:
            self.progress_updated.emit("正在初始化...")
            await task_processor.initialize()
            
            self.progress_updated.emit("正在处理任务...")
            await task_processor.process_all_tasks()
            
            self.progress_updated.emit("任务完成！")
            self.task_completed.emit(True)
            
        except Exception as e:
            logger.error(f"任务处理失败: {e}")
            self.progress_updated.emit(f"任务失败: {str(e)}")
            self.task_completed.emit(False)
        finally:
            await task_processor.cleanup()


class VideoGeneratorGUI(QMainWindow):
    """主GUI窗口"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.setup_logging()
        self.load_default_config()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("ChatGLM视频自动生成工具")
        self.setGeometry(100, 100, 900, 750)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
        """)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("ChatGLM视频自动生成工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 基本配置选项卡
        basic_tab = self.create_basic_config_tab()
        tab_widget.addTab(basic_tab, "基本配置")
        
        # 高级配置选项卡
        advanced_tab = self.create_advanced_config_tab()
        tab_widget.addTab(advanced_tab, "高级配置")
        
        # 日志输出选项卡
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, "日志输出")
        
        # 控制按钮
        control_layout = self.create_control_buttons()
        main_layout.addLayout(control_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪 - 请填写配置信息")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.status_label)
    
    def setup_logging(self):
        """设置日志系统"""
        setup_gui_logging()
        gui_log_handler.log_signal.connect(self.append_log)
    
    def create_basic_config_tab(self):
        """创建基本配置选项卡"""
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(15)
        
        # 任务目录配置
        dir_group = QGroupBox("任务目录配置")
        dir_layout = QFormLayout(dir_group)
        
        self.root_dir_edit = QLineEdit()
        self.root_dir_edit.setPlaceholderText("请选择存放图片和Excel文件的根目录...")
        dir_browse_btn = QPushButton("浏览...")
        dir_browse_btn.clicked.connect(self.browse_root_directory)
        
        dir_row_layout = QHBoxLayout()
        dir_row_layout.addWidget(self.root_dir_edit, 3)
        dir_row_layout.addWidget(dir_browse_btn, 1)
        
        dir_layout.addRow("图片和提示词根目录:", dir_row_layout)
        layout.addWidget(dir_group)
        
        # 比特浏览器配置
        browser_group = QGroupBox("比特浏览器配置")
        browser_layout = QFormLayout(browser_group)
        
        self.browser_id_edit = QLineEdit()
        self.browser_id_edit.setPlaceholderText("请输入比特浏览器窗口ID...")
        self.headless_checkbox = QCheckBox("无头模式运行（隐藏浏览器窗口）")
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1000, 300000)
        self.timeout_spinbox.setSuffix(" 毫秒")
        
        self.video_timeout_spinbox = QSpinBox()
        self.video_timeout_spinbox.setRange(60000, 1800000)
        self.video_timeout_spinbox.setSuffix(" 毫秒")
        
        browser_layout.addRow("比特浏览器窗口ID:", self.browser_id_edit)
        browser_layout.addRow("", self.headless_checkbox)
        browser_layout.addRow("默认超时时间:", self.timeout_spinbox)
        browser_layout.addRow("视频生成超时:", self.video_timeout_spinbox)
        
        layout.addWidget(browser_group)
        
        # Excel配置
        excel_group = QGroupBox("Excel配置")
        excel_layout = QFormLayout(excel_group)
        
        self.prompt_column_spinbox = QSpinBox()
        self.prompt_column_spinbox.setRange(1, 50)
        
        self.status_column_spinbox = QSpinBox()
        self.status_column_spinbox.setRange(1, 50)
        
        self.completed_status_edit = QLineEdit()
        self.completed_status_edit.setPlaceholderText("已生成视频")
        
        excel_layout.addRow("提示词所在列:", self.prompt_column_spinbox)
        excel_layout.addRow("状态所在列:", self.status_column_spinbox)
        excel_layout.addRow("完成状态标记:", self.completed_status_edit)
        
        layout.addWidget(excel_group)
        
        layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area
    
    def create_advanced_config_tab(self):
        """创建高级配置选项卡"""
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(15)
        
        # 视频生成选项
        video_group = QGroupBox("视频生成选项")
        video_layout = QFormLayout(video_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["质量更佳", "速度更快"])
        
        self.framerate_combo = QComboBox()
        self.framerate_combo.addItems(["帧率60", "帧率30"])
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["4k", "1080p"])
        
        video_layout.addRow("画质选择:", self.quality_combo)
        video_layout.addRow("帧率选择:", self.framerate_combo)
        video_layout.addRow("分辨率选择:", self.resolution_combo)
        
        layout.addWidget(video_group)
        
        # 智能延时配置
        delay_group = QGroupBox("智能延时配置（秒）")
        delay_layout = QFormLayout(delay_group)
        
        self.min_delay_spinbox = QDoubleSpinBox()
        self.min_delay_spinbox.setRange(0.1, 10.0)
        self.min_delay_spinbox.setSingleStep(0.1)
        self.min_delay_spinbox.setDecimals(1)
        
        self.max_delay_spinbox = QDoubleSpinBox()
        self.max_delay_spinbox.setRange(0.1, 10.0)
        self.max_delay_spinbox.setSingleStep(0.1)
        self.max_delay_spinbox.setDecimals(1)
        
        self.upload_delay_spinbox = QDoubleSpinBox()
        self.upload_delay_spinbox.setRange(0.1, 10.0)
        self.upload_delay_spinbox.setSingleStep(0.1)
        self.upload_delay_spinbox.setDecimals(1)
        
        self.input_delay_spinbox = QDoubleSpinBox()
        self.input_delay_spinbox.setRange(0.1, 10.0)
        self.input_delay_spinbox.setSingleStep(0.1)
        self.input_delay_spinbox.setDecimals(1)
        
        self.click_delay_spinbox = QDoubleSpinBox()
        self.click_delay_spinbox.setRange(0.1, 10.0)
        self.click_delay_spinbox.setSingleStep(0.1)
        self.click_delay_spinbox.setDecimals(1)
        
        delay_layout.addRow("最小延时:", self.min_delay_spinbox)
        delay_layout.addRow("最大延时:", self.max_delay_spinbox)
        delay_layout.addRow("上传后延时:", self.upload_delay_spinbox)
        delay_layout.addRow("输入后延时:", self.input_delay_spinbox)
        delay_layout.addRow("点击后延时:", self.click_delay_spinbox)
        
        layout.addWidget(delay_group)
        
        # 下载配置
        download_group = QGroupBox("下载配置")
        download_layout = QFormLayout(download_group)
        
        self.download_timeout_spinbox = QSpinBox()
        self.download_timeout_spinbox.setRange(10, 600)
        self.download_timeout_spinbox.setSuffix(" 秒")
        
        download_layout.addRow("下载超时时间:", self.download_timeout_spinbox)
        
        layout.addWidget(download_group)
        
        layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area
    
    def create_log_tab(self):
        """创建日志选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日志显示区域
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 9))
        self.log_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(self.log_text_edit.clear)
        
        save_log_btn = QPushButton("保存日志")
        save_log_btn.clicked.connect(self.save_log)
        
        button_layout.addWidget(clear_log_btn)
        button_layout.addWidget(save_log_btn)
        button_layout.addStretch()
        
        layout.addWidget(self.log_text_edit)
        layout.addLayout(button_layout)
        
        return widget
    
    def save_log(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "log.txt", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text_edit.toPlainText())
                QMessageBox.information(self, "成功", "日志已保存！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存日志失败: {str(e)}")
    
    def create_control_buttons(self):
        """创建控制按钮"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.start_btn = QPushButton("开始生成视频")
        self.start_btn.setStyleSheet("QPushButton { min-width: 120px; padding: 10px; }")
        self.start_btn.clicked.connect(self.start_generation)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; min-width: 80px; }")
        self.stop_btn.clicked.connect(self.stop_generation)
        
        reset_btn = QPushButton("重置为默认配置")
        reset_btn.clicked.connect(self.reset_to_default)
        
        save_preset_btn = QPushButton("保存为预设")
        save_preset_btn.clicked.connect(self.save_preset)
        
        load_preset_btn = QPushButton("加载预设")
        load_preset_btn.clicked.connect(self.load_preset)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addStretch()
        layout.addWidget(reset_btn)
        layout.addWidget(save_preset_btn)
        layout.addWidget(load_preset_btn)
        
        return layout
    
    def browse_root_directory(self):
        """浏览根目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择任务根目录", self.root_dir_edit.text()
        )
        if directory:
            self.root_dir_edit.setText(directory)
    
    def load_default_config(self):
        """加载默认配置"""
        try:
            # 从config_manager获取默认配置
            config = config_manager.get_default_config()
            
            # 基本配置
            self.root_dir_edit.setText(config.get('root_directory', ''))
            self.browser_id_edit.setText(config.get('bit_browser_id', ''))
            self.headless_checkbox.setChecked(config.get('headless', False))
            self.timeout_spinbox.setValue(config.get('timeout', 30000))
            self.video_timeout_spinbox.setValue(config.get('video_generation_timeout', 300000))
            
            # Excel配置
            self.prompt_column_spinbox.setValue(config.get('prompt_column', 3))
            self.status_column_spinbox.setValue(config.get('status_column', 5))
            self.completed_status_edit.setText(config.get('completed_status', '已生成视频'))
            
            # 视频选项
            video_options = config.get('video_options', {})
            self.quality_combo.setCurrentText(video_options.get('quality', '速度更快'))
            self.framerate_combo.setCurrentText(video_options.get('framerate', '帧率60'))
            self.resolution_combo.setCurrentText(video_options.get('resolution', '4k'))
            
            # 智能延时
            smart_delay = config.get('smart_delay', {})
            self.min_delay_spinbox.setValue(smart_delay.get('min', 1.0))
            self.max_delay_spinbox.setValue(smart_delay.get('max', 2.0))
            self.upload_delay_spinbox.setValue(smart_delay.get('upload_after', 2.0))
            self.input_delay_spinbox.setValue(smart_delay.get('input_after', 1.0))
            self.click_delay_spinbox.setValue(smart_delay.get('click_after', 1.5))
            
            # 下载配置
            self.download_timeout_spinbox.setValue(config.get('download_timeout', 60))
            
            logger.info("默认配置加载完成")
            
        except Exception as e:
            error_msg = f"加载默认配置失败: {str(e)}"
            QMessageBox.critical(self, "错误", error_msg)
            logger.error(error_msg)
    
    def reset_to_default(self):
        """重置为默认配置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置所有配置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.load_default_config()
            QMessageBox.information(self, "成功", "配置已重置为默认值！")
    
    def save_preset(self):
        """保存配置预设"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置预设", "config_preset.yaml", "YAML文件 (*.yaml);;所有文件 (*)"
        )
        if file_path:
            try:
                config_data = self.get_config_data()
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                QMessageBox.information(self, "成功", "配置预设已保存！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存预设失败: {str(e)}")
    
    def load_preset(self):
        """加载配置预设"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载配置预设", "", "YAML文件 (*.yaml);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # 更新界面
                self.root_dir_edit.setText(config.get('root_directory', ''))
                self.browser_id_edit.setText(config.get('bit_browser_id', ''))
                self.headless_checkbox.setChecked(config.get('headless', False))
                self.timeout_spinbox.setValue(config.get('timeout', 30000))
                self.video_timeout_spinbox.setValue(config.get('video_generation_timeout', 300000))
                
                self.prompt_column_spinbox.setValue(config.get('prompt_column', 3))
                self.status_column_spinbox.setValue(config.get('status_column', 5))
                self.completed_status_edit.setText(config.get('completed_status', '已生成视频'))
                
                video_options = config.get('video_options', {})
                self.quality_combo.setCurrentText(video_options.get('quality', '速度更快'))
                self.framerate_combo.setCurrentText(video_options.get('framerate', '帧率60'))
                self.resolution_combo.setCurrentText(video_options.get('resolution', '4k'))
                
                smart_delay = config.get('smart_delay', {})
                self.min_delay_spinbox.setValue(smart_delay.get('min', 1.0))
                self.max_delay_spinbox.setValue(smart_delay.get('max', 2.0))
                self.upload_delay_spinbox.setValue(smart_delay.get('upload_after', 2.0))
                self.input_delay_spinbox.setValue(smart_delay.get('input_after', 1.0))
                self.click_delay_spinbox.setValue(smart_delay.get('click_after', 1.5))
                
                self.download_timeout_spinbox.setValue(config.get('download_timeout', 60))
                
                QMessageBox.information(self, "成功", "配置预设已加载！")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载预设失败: {str(e)}")
    
    def get_config_data(self):
        """获取界面配置数据"""
        return {
            'root_directory': self.root_dir_edit.text(),
            'prompt_column': self.prompt_column_spinbox.value(),
            'status_column': self.status_column_spinbox.value(),
            'completed_status': self.completed_status_edit.text(),
            'bit_browser_id': self.browser_id_edit.text(),
            'headless': self.headless_checkbox.isChecked(),
            'timeout': self.timeout_spinbox.value(),
            'video_generation_timeout': self.video_timeout_spinbox.value(),
            'video_options': {
                'quality': self.quality_combo.currentText(),
                'framerate': self.framerate_combo.currentText(),
                'resolution': self.resolution_combo.currentText()
            },
            'smart_delay': {
                'min': self.min_delay_spinbox.value(),
                'max': self.max_delay_spinbox.value(),
                'upload_after': self.upload_delay_spinbox.value(),
                'input_after': self.input_delay_spinbox.value(),
                'click_after': self.click_delay_spinbox.value()
            },
            'download_timeout': self.download_timeout_spinbox.value()
        }
    
    def start_generation(self):
        """开始生成视频"""
        try:
            # 验证配置
            if not self.root_dir_edit.text():
                QMessageBox.warning(self, "警告", "请设置任务根目录！")
                return
            
            if not self.browser_id_edit.text():
                QMessageBox.warning(self, "警告", "请设置比特浏览器窗口ID！")
                return
            
            if not os.path.exists(self.root_dir_edit.text()):
                QMessageBox.warning(self, "警告", "任务根目录不存在！")
                return
            
            # 获取配置数据
            config_data = self.get_config_data()
            
            # 创建并启动工作线程
            self.worker = TaskWorker(config_data)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.task_completed.connect(self.task_finished)
            
            # 设置UI状态
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度条
            
            # 启动线程
            self.worker.start()
            
            self.status_label.setText("正在生成视频...")
            logger.info("开始视频生成任务")
            
        except Exception as e:
            error_msg = f"启动失败: {str(e)}"
            QMessageBox.critical(self, "错误", error_msg)
            logger.error(error_msg)
    
    def stop_generation(self):
        """停止生成"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.task_finished(False)
        self.status_label.setText("任务已停止")
        logger.info("任务已停止")
    
    def update_progress(self, message):
        """更新进度"""
        self.status_label.setText(message)
    
    def task_finished(self, success):
        """任务完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("视频生成完成！")
            QMessageBox.information(self, "成功", "视频生成任务已完成！")
            logger.info("视频生成任务已完成")
        else:
            self.status_label.setText("任务失败或被停止")
    
    def append_log(self, message):
        """添加日志消息"""
        self.log_text_edit.append(message)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("ChatGLM视频生成工具")
    app.setApplicationVersion("1.0")
    
    # 创建主窗口
    window = VideoGeneratorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 