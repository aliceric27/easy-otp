"""
Easy OTP 打包腳本
使用 PyInstaller 打包成單一執行檔
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """清理建構目錄"""
    print("清理舊的建構檔案...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已刪除 {dir_name}/")
    
    for pattern in files_to_remove:
        import glob
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"  已刪除 {file}")


def create_icon():
    """創建應用程式圖標"""
    print("創建應用程式圖標...")
    
    # 如果沒有圖標檔案，創建一個簡單的圖標
    icon_path = Path("src/assets/icon.ico")
    if not icon_path.exists():
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 創建圖標圖片
            size = 256
            img = Image.new('RGBA', (size, size), (14, 17, 23, 255))  # 深色背景
            draw = ImageDraw.Draw(img)
            
            # 繪製圓形背景
            margin = 20
            draw.ellipse(
                [(margin, margin), (size-margin, size-margin)],
                fill=(59, 130, 246, 255)  # 藍色
            )
            
            # 繪製鎖圖標
            try:
                font = ImageFont.truetype("arial.ttf", 120)
            except:
                font = ImageFont.load_default()
            
            text = "🔐"
            # 獲取文字邊界框
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 計算居中位置
            x = (size - text_width) // 2
            y = (size - text_height) // 2 - 10
            
            draw.text((x, y), text, fill='white', font=font)
            
            # 儲存為 ICO
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"  已創建圖標: {icon_path}")
            
        except Exception as e:
            print(f"  創建圖標失敗: {e}")
            return None
    
    return str(icon_path)


def create_spec_file(icon_path=None):
    """創建 PyInstaller spec 檔案"""
    print("創建 spec 檔案...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import site

# 動態尋找 pyzbar DLL 檔案
pyzbar_path = None
for site_dir in site.getsitepackages():
    test_path = os.path.join(site_dir, 'pyzbar')
    if os.path.exists(test_path):
        pyzbar_path = test_path
        break

# 如果找不到，嘗試使用固定路徑
if not pyzbar_path:
    import pyzbar
    pyzbar_path = os.path.dirname(pyzbar.__file__)

# 收集 pyzbar DLL 檔案
pyzbar_binaries = []
if os.path.exists(pyzbar_path):
    for dll_file in ['libiconv.dll', 'libzbar-64.dll']:
        dll_path = os.path.join(pyzbar_path, dll_file)
        if os.path.exists(dll_path):
            pyzbar_binaries.append((dll_path, '.'))
            print(f"  找到 DLL: {{dll_file}}")

if not pyzbar_binaries:
    print("  警告: 未找到 pyzbar DLL 檔案，可能導致打包後無法使用 QR Code 功能")

a = Analysis(
    ['easy_otp.py'],
    pathex=[],
    binaries=pyzbar_binaries,
    datas=[
        ('src/assets', 'assets'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'customtkinter',
        'darkdetect',
        'pyotp',
        'qrcode',
        'pyzbar',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EasyOTP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {f'icon=r"{icon_path}",' if icon_path else ''}
)
'''
    
    with open('EasyOTP.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("  已創建 EasyOTP.spec")


def install_dependencies():
    """安裝依賴"""
    print("檢查並安裝依賴...")
    
    # 檢查 pip
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      check=True, capture_output=True)
    except:
        print("錯誤: 未找到 pip，請先安裝 pip")
        return False
    
    # 安裝依賴
    print("  安裝 requirements.txt 中的依賴...")
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"錯誤: 安裝依賴失敗\n{result.stderr}")
        return False
    
    print("  依賴安裝完成")
    return True


def build_exe():
    """建構執行檔"""
    print("開始建構執行檔...")
    
    # 使用 spec 檔案建構
    cmd = ['pyinstaller', 'EasyOTP.spec', '--clean']
    
    print(f"  執行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"錯誤: 建構失敗\n{result.stderr}")
        return False
    
    print("  建構完成")
    return True


def post_build():
    """建構後處理"""
    print("執行建構後處理...")
    
    # 檢查輸出檔案
    exe_path = Path('dist/EasyOTP.exe')
    if not exe_path.exists():
        print("錯誤: 找不到輸出的執行檔")
        return False
    
    # 顯示檔案資訊
    file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    print(f"  執行檔路徑: {exe_path.absolute()}")
    print(f"  檔案大小: {file_size:.2f} MB")
    
    # 創建 README
    readme_content = """# Easy OTP

現代化的 OTP 管理器

## 功能特點

- 🔐 安全的本地儲存
- 📷 QR Code 掃描導入
- 🎨 現代化深色界面
- ⏱️ 視覺化倒數計時
- 📤 多格式導出功能
- 🔍 即時搜尋
- 📋 一鍵複製

## 使用說明

1. 執行 EasyOTP.exe
2. 點擊「新增」按鈕導入 OTP
3. 點擊 OTP 代碼即可複製

## 注意事項

- Windows 可能需要安裝 Visual C++ Redistributable
- 首次執行可能被防毒軟體誤報，請新增信任
"""
    
    readme_path = Path('dist/README.txt')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("  已創建 README.txt")
    return True


def main():
    """主函數"""
    print("=== Easy OTP 打包腳本 ===\n")
    
    # 切換到專案根目錄
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 執行步驟
    steps = [
        ("清理舊檔案", clean_build),
        ("安裝依賴", install_dependencies),
        ("創建圖標", create_icon),
        ("創建 spec 檔案", lambda: create_spec_file(create_icon())),
        ("建構執行檔", build_exe),
        ("後處理", post_build)
    ]
    
    for step_name, step_func in steps:
        print(f"\n[步驟] {step_name}")
        print("-" * 40)
        
        try:
            result = step_func()
            if result is False:
                print(f"\n❌ {step_name} 失敗")
                return 1
        except Exception as e:
            print(f"\n❌ {step_name} 發生錯誤: {e}")
            return 1
    
    print("\n" + "=" * 40)
    print("✅ 打包完成！")
    print(f"執行檔位置: {Path('dist/EasyOTP.exe').absolute()}")
    print("=" * 40)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())