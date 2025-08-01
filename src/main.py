"""
Easy OTP - 主程式入口
"""
import sys
import os

# 將專案根目錄加入 Python 路徑，確保可以正確導入所有模組
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.ui.main_window import MainWindow


def main():
    """主函數"""
    # 創建並運行應用程式
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()