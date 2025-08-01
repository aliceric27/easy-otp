"""
國際化 (i18n) 語言管理系統
使用單例模式和觀察者模式實現語言切換功能
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from threading import Lock


class LanguageManager:
    """語言管理器 (單例模式)"""
    
    _instance = None
    _lock = Lock()
    
    # 語言代碼驗證模式
    VALID_LANGUAGE_PATTERN = re.compile(r'^[a-zA-Z]{2}_[a-zA-Z]{2}$')
    
    def __new__(cls):
        """確保單例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化語言管理器"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._current_language = "zh_TW"  # 預設繁體中文
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._observers: List[Callable[[str], None]] = []
        
        # 設定翻譯檔案目錄
        self._setup_locales_directory()
        
        # 已允許的語言列表（白名單）
        self._allowed_languages = set()
        
        # 載入預設語言
        self._load_language(self._current_language)
    
    def _setup_locales_directory(self):
        """設定翻譯檔案目錄"""
        # 取得專案根目錄
        current = Path(__file__).parent
        project_root = current.parent.parent  # src/utils -> src -> project_root
        
        self._locales_dir = project_root / "src" / "assets" / "locales"
        self._locales_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_language_code(self, code: str) -> bool:
        """
        驗證語言代碼格式
        
        Args:
            code: 語言代碼
            
        Returns:
            bool: 是否有效
        """
        if not code or not isinstance(code, str):
            return False
        
        # 優先檢查白名單
        if self._allowed_languages and code in self._allowed_languages:
            return True
        
        # 檢查格式
        return bool(self.VALID_LANGUAGE_PATTERN.match(code))
    
    def _load_language(self, language_code: str) -> bool:
        """
        載入指定語言的翻譯檔案
        
        Args:
            language_code: 語言代碼 (如 zh_TW, en_US)
            
        Returns:
            bool: 是否載入成功
        """
        # 驗證語言代碼
        if not self._validate_language_code(language_code):
            print(f"警告: 無效的語言代碼 {language_code}")
            return False
        
        try:
            locale_file = self._locales_dir / f"{language_code}.json"
            
            if not locale_file.exists():
                print(f"警告: 翻譯檔案 {locale_file} 不存在")
                return False
            
            with open(locale_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            self._translations[language_code] = translations
            # 加入允許列表
            self._allowed_languages.add(language_code)
            return True
            
        except Exception as e:
            print(f"載入語言檔案失敗: {e}")
            return False
    
    def set_language(self, language_code: str) -> bool:
        """
        設定當前語言
        
        Args:
            language_code: 語言代碼
            
        Returns:
            bool: 是否設定成功
        """
        # 驗證語言代碼
        if not self._validate_language_code(language_code):
            print(f"警告: 無效的語言代碼 {language_code}")
            return False
        
        # 如果語言未載入，先載入
        if language_code not in self._translations:
            if not self._load_language(language_code):
                return False
        
        # 設定當前語言
        old_language = self._current_language
        self._current_language = language_code
        
        # 通知所有觀察者
        self._notify_observers(old_language)
        
        return True
    
    def get_current_language(self) -> str:
        """
        取得當前語言代碼
        
        Returns:
            str: 當前語言代碼
        """
        return self._current_language
    
    def get_available_languages(self) -> List[str]:
        """
        取得可用的語言列表
        
        Returns:
            List[str]: 可用語言代碼列表
        """
        languages = []
        
        # 掃描翻譯檔案目錄
        if self._locales_dir.exists():
            for file in self._locales_dir.glob("*.json"):
                language_code = file.stem
                # 驗證語言代碼格式
                if self._validate_language_code(language_code):
                    languages.append(language_code)
                    # 加入允許列表
                    self._allowed_languages.add(language_code)
        
        return sorted(languages)
    
    def t(self, key: str, **kwargs) -> str:
        """
        取得翻譯文字
        
        Args:
            key: 翻譯鍵值，支援巢狀鍵值如 "menu.file.open"
            **kwargs: 用於字串格式化的參數
            
        Returns:
            str: 翻譯後的文字
        """
        try:
            # 取得當前語言的翻譯
            translations = self._translations.get(self._current_language, {})
            
            # 處理巢狀鍵值
            keys = key.split('.')
            value = translations
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # 如果找不到翻譯，回傳鍵值本身
                    return key
            
            # 如果值不是字串，回傳鍵值
            if not isinstance(value, str):
                return key
            
            # 進行字串格式化
            if kwargs:
                try:
                    return value.format(**kwargs)
                except (KeyError, ValueError):
                    # 格式化失敗，回傳原始值
                    return value
            
            return value
            
        except Exception as e:
            print(f"翻譯失敗 '{key}': {e}")
            return key
    
    def add_observer(self, callback: Callable[[str], None]) -> None:
        """
        新增語言變更觀察者
        
        Args:
            callback: 回調函數，會接收舊語言代碼作為參數
        """
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable[[str], None]) -> None:
        """
        移除語言變更觀察者
        
        Args:
            callback: 要移除的回調函數
        """
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self, old_language: str) -> None:
        """
        通知所有觀察者語言已變更
        
        Args:
            old_language: 舊語言代碼
        """
        for callback in self._observers[:]:  # 複製列表避免迭代時修改
            try:
                callback(old_language)
            except Exception as e:
                print(f"語言變更通知失敗: {e}")
    
    def reload_language(self, language_code: Optional[str] = None) -> bool:
        """
        重新載入語言檔案
        
        Args:
            language_code: 要重新載入的語言代碼，None 表示當前語言
            
        Returns:
            bool: 是否重新載入成功
        """
        if language_code is None:
            language_code = self._current_language
        
        # 清除快取
        if language_code in self._translations:
            del self._translations[language_code]
        
        # 重新載入
        success = self._load_language(language_code)
        
        # 如果是當前語言，通知觀察者
        if success and language_code == self._current_language:
            self._notify_observers(self._current_language)
        
        return success
    
    def get_language_name(self, language_code: str) -> str:
        """
        取得語言的顯示名稱
        
        Args:
            language_code: 語言代碼
            
        Returns:
            str: 語言顯示名稱
        """
        # 語言名稱映射
        language_names = {
            "zh_TW": "繁體中文",
            "zh_CN": "简体中文", 
            "en_US": "English",
            "ja_JP": "日本語",
            "ko_KR": "한국어"
        }
        
        return language_names.get(language_code, language_code)


# 創建全域實例
i18n = LanguageManager()


# 便利函數
def t(key: str, **kwargs) -> str:
    """
    快速翻譯函數
    
    Args:
        key: 翻譯鍵值
        **kwargs: 格式化參數
        
    Returns:
        str: 翻譯文字
    """
    return i18n.t(key, **kwargs)


def set_language(language_code: str) -> bool:
    """
    設定語言
    
    Args:
        language_code: 語言代碼
        
    Returns:
        bool: 是否設定成功
    """
    return i18n.set_language(language_code)


def get_current_language() -> str:
    """
    取得當前語言
    
    Returns:
        str: 當前語言代碼
    """
    return i18n.get_current_language()


def add_language_observer(callback: Callable[[str], None]) -> None:
    """
    新增語言變更觀察者
    
    Args:
        callback: 回調函數
    """
    i18n.add_observer(callback)


def remove_language_observer(callback: Callable[[str], None]) -> None:
    """
    移除語言變更觀察者
    
    Args:
        callback: 回調函數
    """
    i18n.remove_observer(callback)