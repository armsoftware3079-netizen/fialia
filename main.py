import os
import random
import string
import shutil
import zipfile
import tempfile
import configparser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QFileDialog, QStatusBar, QGroupBox, 
    QFrame, QTextEdit, QAction
)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QBrush, QPixmap
from PyQt5.QtCore import Qt
import sys

class EncodeWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowTitle('Encode - Fialia')
        self.resize(600, 300)
        self.setWindowIcon(QIcon(os.path.join(self.current_dir, 'res', 'icon', 'Fialia.png')))
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('准备就绪')
        self.cw = QWidget()  # central_widget
        self.setCentralWidget(self.cw)
        self.ml = QVBoxLayout(self.cw)  # main_layout
        self.create_encryption_group()
        self.set_light_theme()
    
    def set_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(220, 220, 220))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 0, 255))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
    
    def create_encryption_group(self):
        group = QGroupBox('文件加密')
        group_layout = QVBoxLayout()
        file_layout = QHBoxLayout()
        self.efp = QLabel('未选择文件')  # encrypt_file_path
        self.efp.setMinimumWidth(250)
        self.efp.setWordWrap(True)
        select_file_btn = QPushButton('选择文件')
        select_file_btn.clicked.connect(self.select_file_to_encrypt)
        file_layout.addWidget(select_file_btn)
        file_layout.addWidget(self.efp)
        key_layout = QHBoxLayout()
        self.ek = QLineEdit('点击生成随机密钥')  # encrypt_key
        self.ek.setReadOnly(True)
        generate_key_btn = QPushButton('生成')
        generate_key_btn.clicked.connect(self.generate_key)
        key_layout.addWidget(self.ek)
        key_layout.addWidget(generate_key_btn)
        custom_name_layout = QHBoxLayout()
        custom_name_layout.addWidget(QLabel('自定义文件名（可选）：'))
        self.cen = QLineEdit()  # custom_encrypt_name
        self.cen.setPlaceholderText('不填则使用原文件名')
        custom_name_layout.addWidget(self.cen)
        start_encrypt_btn = QPushButton('开始加密')
        start_encrypt_btn.clicked.connect(self.start_encryption)
        group_layout.addLayout(file_layout)
        group_layout.addLayout(key_layout)
        group_layout.addLayout(custom_name_layout)
        group_layout.addWidget(start_encrypt_btn)
        group.setLayout(group_layout)
        self.ml.addWidget(group)
    
    def select_file_to_encrypt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择要加密的文件', '', '所有文件 (*.*)')
        if file_path:
            self.efp.setText(file_path)
            self.statusBar.showMessage(f'已选择文件: {file_path}')
    
    def generate_key(self):
        chars = list(string.digits + string.ascii_lowercase)
        random.shuffle(chars)
        key = ''.join(chars[:36])
        self.ek.setText(key)
        self.statusBar.showMessage('已生成随机密钥')
    
    def start_encryption(self):
        file_path = self.efp.text()
        key = self.ek.text()
        if file_path == '未选择文件':
            self.statusBar.showMessage('请先选择要加密的文件')
            return
        if key == '点击生成随机密钥':
            self.statusBar.showMessage('请先生成密钥')
            return
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with open(file_path, 'rb') as f:
                    data = f.read()
                csz = len(data) // 36  # chunk_size
                rem = len(data) % 36  # remainder
                chunks = []
                for i in range(36):
                    start = i * csz
                    end = start + csz + (rem if i == 35 else 0)
                    chunks.append(data[start:end])
                kim = {char: i for i, char in enumerate(key)}  # key_index_map
                sc = sorted(key)  # sorted_chars
                rc = [chunks[kim[char]] for char in sc]  # reordered_chunks
                for i, chunk in enumerate(rc):
                    cfp = os.path.join(temp_dir, f'{i}.fbk')  # chunk_file_path
                    with open(cfp, 'wb') as f:
                        f.write(chunk)
                oe = os.path.splitext(file_path)[1]  # original_ext
                cp = os.path.join(temp_dir, 'config.ini')  # config_path
                config = configparser.ConfigParser()
                config['FileInfo'] = {'tail': oe.lstrip('.')}
                with open(cp, 'w') as f:
                    config.write(f)
                zfp = f'{file_path}.zip'  # zip_file_path
                with zipfile.ZipFile(zfp, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i in range(36):
                        fbk_file = os.path.join(temp_dir, f'{i}.fbk')
                        zipf.write(fbk_file, f'{i}.fbk')
                    zipf.write(cp, 'config.ini')
                cn = self.cen.text().strip()  # custom_name
                if cn:
                    fd = os.path.dirname(file_path)  # file_dir
                    ffp = os.path.join(fd, f'{cn}.fpk')  # fpk_file_path
                else:
                    ffp = f'{file_path}.fpk'  # fpk_file_path
                if os.path.exists(ffp):
                    os.remove(ffp)
                os.rename(zfp, ffp)
            self.statusBar.showMessage(f'文件加密成功，已保存到: {ffp}')
        except Exception as e:
            self.statusBar.showMessage(f'加密失败: {str(e)}')

class DecodeWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowTitle('Decode - Fialia')
        self.resize(600, 350)
        self.setWindowIcon(QIcon(os.path.join(self.current_dir, 'res', 'icon', 'Fialia.png')))
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('准备就绪')
        self.cw = QWidget()  # central_widget
        self.setCentralWidget(self.cw)
        self.ml = QVBoxLayout(self.cw)  # main_layout
        self.create_decryption_group()
        self.set_light_theme()
    
    def set_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(220, 220, 220))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 0, 255))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
    
    def create_decryption_group(self):
        group = QGroupBox('文件解密')
        group_layout = QVBoxLayout()
        dir_layout = QHBoxLayout()
        self.ddp = QLabel('未选择加密文件')  # decrypt_dir_path
        self.ddp.setMinimumWidth(250)
        self.ddp.setWordWrap(True)
        select_dir_btn = QPushButton('选择加密文件')
        select_dir_btn.clicked.connect(self.select_directory_to_decrypt)
        dir_layout.addWidget(select_dir_btn)
        dir_layout.addWidget(self.ddp)
        key_layout = QHBoxLayout()
        self.decrypt_key = QLineEdit()
        self.decrypt_key.setPlaceholderText('输入解密密钥')
        key_layout.addWidget(self.decrypt_key)
        output_layout = QHBoxLayout()
        self.odp = QLabel('未选择输出目录')  # output_dir_path
        self.odp.setMinimumWidth(250)
        self.odp.setWordWrap(True)
        select_output_btn = QPushButton('选择目录')
        select_output_btn.clicked.connect(self.select_output_directory)
        output_layout.addWidget(select_output_btn)
        output_layout.addWidget(self.odp)
        custom_name_layout = QHBoxLayout()
        custom_name_layout.addWidget(QLabel('自定义文件名（可选）：'))
        self.cdn = QLineEdit()  # custom_decrypt_name
        self.cdn.setPlaceholderText('不填则使用原文件名')
        custom_name_layout.addWidget(self.cdn)
        start_decrypt_btn = QPushButton('开始解密')
        start_decrypt_btn.clicked.connect(self.start_decryption)
        group_layout.addLayout(dir_layout)
        group_layout.addLayout(key_layout)
        group_layout.addLayout(output_layout)
        group_layout.addLayout(custom_name_layout)
        group_layout.addWidget(start_decrypt_btn)
        group.setLayout(group_layout)
        self.ml.addWidget(group)
    
    def select_directory_to_decrypt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择.fpk加密文件', '', 'Fialia加密文件 (*.fpk)')
        if file_path:
            self.ddp.setText(file_path)
            self.statusBar.showMessage(f'已选择加密文件: {file_path}')
    
    def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择输出目录', '')
        if dir_path:
            self.odp.setText(dir_path)
            self.statusBar.showMessage(f'已选择输出目录: {dir_path}')
    
    def start_decryption(self):
        ffp = self.ddp.text()  # fpk_file_path
        key = self.decrypt_key.text()
        od = self.odp.text()  # output_dir
        if ffp == '未选择加密文件':
            self.statusBar.showMessage('请先选择.fpk加密文件')
            return
        if not key:
            self.statusBar.showMessage('请输入解密密钥')
            return
        if od == '未选择输出目录':
            self.statusBar.showMessage('请先选择输出目录')
            return
        try:
            if len(key) != 36 or not all(c in string.digits + string.ascii_lowercase for c in key) or len(set(key)) != 36:
                self.statusBar.showMessage('密钥错误: 密钥必须是36位不重复的0-9和a-z字符')
                return
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(ffp, 'r') as zipf:
                    zipf.extractall(temp_dir)
                cp = os.path.join(temp_dir, 'config.ini')  # config_path
                if not os.path.exists(cp):
                    self.statusBar.showMessage('解密失败: 找不到config.ini文件')
                    return
                config = configparser.ConfigParser()
                config.read(cp)
                tail = config['FileInfo'].get('tail', '')
                chunks = []
                for i in range(36):
                    cfp = os.path.join(temp_dir, f'{i}.fbk')  # chunk_file_path
                    if not os.path.exists(cfp):
                        self.statusBar.showMessage(f'解密失败: 找不到块文件 {i}.fbk')
                        return
                    with open(cfp, 'rb') as f:
                        chunks.append(f.read())
            kim = {char: i for i, char in enumerate(key)}  # key_index_map
            sc = sorted(key)  # sorted_chars
            ooc = [None] * 36  # original_order_chunks
            for i, char in enumerate(sc):
                ooc[kim[char]] = chunks[i]
            md = b''.join(ooc)  # merged_data
            cn = self.cdn.text().strip()  # custom_name
            if cn:
                if tail:
                    ofn = f'{cn}.{tail}'  # output_file_name
                else:
                    ofn = cn  # output_file_name
            else:
                bn = os.path.splitext(os.path.basename(ffp))[0]  # base_name
                if tail:
                    ofn = f'{bn}.{tail}'  # output_file_name
                else:
                    ofn = bn  # output_file_name
            op = os.path.join(od, ofn)  # output_path
            with open(op, 'wb') as f:
                f.write(md)
            self.statusBar.showMessage(f'文件解密成功，已保存到: {op}')
        except Exception as e:
            self.statusBar.showMessage(f'解密失败: {str(e)}')

class FialiaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(self.current_dir, 'res', 'icon', 'Fialia.png')
        self.setWindowTitle('Fialia')
        self.resize(800, 600)
        self.create_menu_bar()
        self.setWindowIcon(QIcon(self.icon_path))
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('欢迎使用Fialia')
        self.cw = QWidget()  # central_widget
        self.setCentralWidget(self.cw)
        self.ml = QVBoxLayout(self.cw)  # main_layout
        ll = QHBoxLayout()  # logo_layout
        ll.setContentsMargins(10, -10, 10, 10)
        f2p = os.path.join(self.current_dir, 'res', 'icon', 'Fia2_resized.png')  # fia2_path
        if os.path.exists(f2p):
            self.llb = QLabel()  # logo_label
            self.llb.setPixmap(QPixmap(f2p))
            self.llb.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            ll.addWidget(self.llb)
        else:
            self.statusBar.showMessage('警告: 找不到Fia2_resized.png图标')
        ll.addStretch()
        self.ml.addLayout(ll)
        self.create_readme_edit()
        self.create_function_buttons()
        self.set_light_theme()
        self.ew = None  # encode_window
        self.dw = None  # decode_window
    
    def set_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(220, 220, 220))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 0, 255))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
        self.set_background_image()
        
    def set_background_image(self):
        background_path = os.path.join(self.current_dir, 'res', 'icon', 'background1.png')
        if os.path.exists(background_path):
            central_widget = self.centralWidget()
            if central_widget:
                palette = central_widget.palette()
                brush = QBrush(QPixmap(background_path).scaled(central_widget.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                palette.setBrush(QPalette.Window, brush)
                central_widget.setAutoFillBackground(True)
                central_widget.setPalette(palette)
        else:
            self.statusBar.showMessage('警告: 找不到背景图片')
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_background_image()
    
    def create_readme_edit(self):
        self.re = QTextEdit()  # readme_edit
        self.re.setReadOnly(True)
        readme_content = """Fialia 应用程序说明

为何选择 Fialia？
- Fialia 作为一个文件加密程序，主旨在于混淆与重组，而非传统压缩。相对于传统压缩软件，Fialia 生成的 fpk 文件内不包含密钥，错误的密钥只会获得不可用的文件。
- Fialia 作为轻量化且开源的，集成压缩和加密的轻量化应用程序，体积小且用处大，适合开发人员。
- Fialia 开发团队咨询过用户意见，对于现役的软件开发人员，Fialia 为他们提供了极大的便利，某开发人员表示：服务器的发信系统终于不用炸了。

如何开始？
- Fialia 拥有便捷的 UI 界面，用户只需轻触按钮即可。
- Fialia 内置双窗口，分别为编码窗口和解码窗口，用户可以根据需要选择使用。
"""
        self.re.setPlainText(readme_content)
        font = QFont()
        font.setPointSize(11)
        self.re.setFont(font)
        self.ml.addWidget(self.re)
    
    def create_function_buttons(self):
        bl = QHBoxLayout()  # buttons_layout
        eb = QPushButton('打开编码窗口')  # encode_btn
        eb.setMinimumHeight(40)
        eb.clicked.connect(self.open_encode_window)
        db = QPushButton('打开解码窗口')  # decode_btn
        db.setMinimumHeight(40)
        db.clicked.connect(self.open_decode_window)
        bl.addWidget(eb)
        bl.addWidget(db)
        bl.setAlignment(Qt.AlignCenter)
        self.ml.addLayout(bl)
        
    def create_menu_bar(self):
        mb = self.menuBar()  # menu_bar
        tm = mb.addMenu('Tools')  # tools_menu
        ea = QAction('Encode', self)  # encode_action
        ea.triggered.connect(self.open_encode_window)
        tm.addAction(ea)
        da = QAction('Decode', self)  # decode_action
        da.triggered.connect(self.open_decode_window)
        tm.addAction(da)
        cm = mb.addMenu('Config')  # config_menu
        oca = QAction('Open Config', self)  # open_config_action
        oca.triggered.connect(self.open_config_window)
        cm.addAction(oca)
        
    def open_config_window(self):
        cw = QMainWindow(self)  # config_window
        cw.setWindowTitle('Config')
        cw.resize(600, 400)
        cw.setWindowIcon(QIcon(self.icon_path))
        central_widget = QWidget()
        cw.setCentralWidget(central_widget)
        l = QVBoxLayout(central_widget)  # layout
        hl = QLabel('Config窗口功能将在后续版本中实现', central_widget)  # hint_label
        hl.setAlignment(Qt.AlignCenter)
        l.addWidget(hl)
        cw.show()
    
    def open_encode_window(self):
        if self.ew is None or not self.ew.isVisible():
            self.ew = EncodeWindow(self)  # encode_window
            self.ew.show()
        else:
            self.ew.raise_()
        
    def open_decode_window(self):
        if self.dw is None or not self.dw.isVisible():
            self.dw = DecodeWindow(self)  # decode_window
            self.dw.show()
        else:
            self.dw.raise_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FialiaApp()
    window.show()
    sys.exit(app.exec_())