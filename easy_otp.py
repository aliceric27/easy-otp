"""
Easy OTP - PyInstaller 入口點
"""
from src.ui.main_window import MainWindow


def main():
    """主函數"""
    # 創建並運行應用程式
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()