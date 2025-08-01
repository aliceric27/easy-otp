"""
應用程式設定管理
處理使用者偏好設定的儲存和載入
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock


class SettingsManager:
    """設定管理器"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """確保單例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化設定管理器
        
        Args:
            data_dir: 資料目錄路徑，預設為使用者設定目錄
        """
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # 設定資料目錄
        if data_dir is None:
            # 使用使用者的應用資料目錄
            app_name = "EasyOTP"
            if os.name == 'nt':  # Windows
                base_dir = os.environ.get('APPDATA', '.')
            else:  # macOS/Linux
                base_dir = os.path.expanduser('~/.config')
            
            self.data_dir = Path(base_dir) / app_name
        else:
            self.data_dir = Path(data_dir)
        
        # 創建資料目錄
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 設定檔案路徑
        self.settings_file = self.data_dir / "settings.json"
        
        # 預設設定
        self.default_settings = {
            "language": "zh_TW",  # 預設語言
            "theme": "dark",      # 主題
            "window": {
                "width": 450,
                "height": 700,
                "x": None,       # 視窗位置
                "y": None
            },
            "auto_backup": True,  # 自動備份
            "backup_count": 10,   # 備份保留數量
            "show_progress": True,  # 顯示進度條
            "auto_copy": False,   # 自動複製 OTP
            "notifications": {
                "enabled": True,
                "sound": False
            },
            "security": {
                "auto_lock": False,  # 自動鎖定
                "lock_timeout": 300, # 鎖定超時時間（秒）
                "require_password": False  # 需要密碼
            }
        }
        
        # 當前設定
        self._settings: Dict[str, Any] = {}
        
        # 載入設定
        self.load()
    
    def load(self) -> bool:
        """
        載入設定
        
        Returns:
            bool: 是否載入成功
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 合併預設設定和載入的設定
                self._settings = self._merge_settings(self.default_settings, loaded_settings)
            else:
                # 使用預設設定
                self._settings = self.default_settings.copy()
            
            return True
            
        except Exception as e:
            print(f"載入設定失敗: {e}")
            # 使用預設設定
            self._settings = self.default_settings.copy()
            return False
    
    def save(self) -> bool:
        """
        儲存設定
        
        Returns:
            bool: 是否儲存成功
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"儲存設定失敗: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        取得設定值
        
        Args:
            key: 設定鍵值，支援巢狀鍵值如 "window.width"
            default: 預設值
            
        Returns:
            Any: 設定值
        """
        try:
            keys = key.split('.')
            value = self._settings
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any, save_immediately: bool = True) -> bool:
        """
        設定值
        
        Args:
            key: 設定鍵值，支援巢狀鍵值如 "window.width"
            value: 設定值
            save_immediately: 是否立即儲存
            
        Returns:
            bool: 是否設定成功
        """
        try:
            keys = key.split('.')
            current = self._settings
            
            # 導航到最後一層
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                elif not isinstance(current[k], dict):
                    # 如果不是字典，無法設定巢狀值
                    return False
                current = current[k]
            
            # 設定值
            current[keys[-1]] = value
            
            # 立即儲存
            if save_immediately:
                return self.save()
            
            return True
            
        except Exception as e:
            print(f"設定值失敗 '{key}': {e}")
            return False
    
    def get_language(self) -> str:
        """
        取得語言設定
        
        Returns:
            str: 語言代碼
        """
        return self.get("language", "zh_TW")
    
    def set_language(self, language_code: str) -> bool:
        """
        設定語言
        
        Args:
            language_code: 語言代碼
            
        Returns:
            bool: 是否設定成功
        """
        return self.set("language", language_code)
    
    def get_window_settings(self) -> Dict[str, Any]:
        """
        取得視窗設定
        
        Returns:
            Dict[str, Any]: 視窗設定
        """
        return self.get("window", self.default_settings["window"])
    
    def set_window_settings(self, width: int, height: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        設定視窗大小和位置
        
        Args:
            width: 視窗寬度
            height: 視窗高度
            x: 視窗 X 座標
            y: 視窗 Y 座標
            
        Returns:
            bool: 是否設定成功
        """
        window_settings = {
            "width": width,
            "height": height,
            "x": x,
            "y": y
        }
        
        return self.set("window", window_settings)
    
    def reset_to_defaults(self) -> bool:
        """
        重設為預設設定
        
        Returns:
            bool: 是否重設成功
        """
        try:
            self._settings = self.default_settings.copy()
            return self.save()
        except Exception as e:
            print(f"重設設定失敗: {e}")
            return False
    
    def _merge_settings(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併設定（遞迴合併巢狀字典）
        
        Args:
            default: 預設設定
            loaded: 載入的設定
            
        Returns:
            Dict[str, Any]: 合併後的設定
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 遞迴合併巢狀字典
                result[key] = self._merge_settings(result[key], value)
            else:
                # 直接設定值
                result[key] = value
        
        return result
    
    def export_settings(self, file_path: str) -> bool:
        """
        導出設定到檔案
        
        Args:
            file_path: 導出檔案路徑
            
        Returns:
            bool: 是否導出成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"導出設定失敗: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        從檔案導入設定
        
        Args:
            file_path: 導入檔案路徑
            
        Returns:
            bool: 是否導入成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # 合併設定
            self._settings = self._merge_settings(self.default_settings, imported_settings)
            
            # 儲存合併後的設定
            return self.save()
            
        except Exception as e:
            print(f"導入設定失敗: {e}")
            return False


# 創建全域實例
settings = SettingsManager()