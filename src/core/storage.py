"""
資料儲存管理模組
處理 OTP 資料的本地儲存和載入
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from src.core.otp_manager import OTPEntry, OTPManager


class StorageManager:
    """儲存管理器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化儲存管理器
        
        Args:
            data_dir: 資料目錄路徑，預設為使用者資料目錄
        """
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
        
        # 資料檔案路徑
        self.data_file = self.data_dir / "otp_data.json"
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def save(self, otp_manager: OTPManager) -> bool:
        """
        儲存 OTP 資料
        
        Args:
            otp_manager: OTP 管理器實例
            
        Returns:
            bool: 是否儲存成功
        """
        try:
            # 準備資料
            data = {
                "version": "2.0",
                "updated_at": datetime.now().isoformat(),
                "entries": []
            }
            
            # 轉換條目為可序列化格式
            for entry in otp_manager.get_all_entries():
                entry_data = {
                    "label": entry.label,
                    "secret": entry.secret,
                    "issuer": entry.issuer,
                    "algorithm": entry.algorithm,
                    "digits": entry.digits,
                    "period": entry.period,
                    "tags": entry.tags,
                    "created_at": entry.created_at.isoformat()
                }
                data["entries"].append(entry_data)
            
            # 創建備份
            if self.data_file.exists():
                self._create_backup()
            
            # 寫入檔案
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"儲存失敗: {e}")
            return False
    
    def load(self) -> Optional[OTPManager]:
        """
        載入 OTP 資料
        
        Returns:
            Optional[OTPManager]: OTP 管理器實例或 None
        """
        if not self.data_file.exists():
            return OTPManager()
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            otp_manager = OTPManager()
            
            # 相容舊版本
            if isinstance(data, list):
                # 舊版本格式
                for item in data:
                    entry = OTPEntry(
                        label=item.get("label", "Unknown"),
                        secret=item.get("secret", ""),
                        created_at=datetime.now()
                    )
                    otp_manager.add_entry(entry)
            else:
                # 新版本格式
                for item in data.get("entries", []):
                    created_at = item.get("created_at")
                    if created_at:
                        created_at = datetime.fromisoformat(created_at)
                    else:
                        created_at = datetime.now()
                    
                    entry = OTPEntry(
                        label=item.get("label", "Unknown"),
                        secret=item.get("secret", ""),
                        issuer=item.get("issuer"),
                        algorithm=item.get("algorithm", "SHA1"),
                        digits=item.get("digits", 6),
                        period=item.get("period", 30),
                        tags=item.get("tags", []),
                        created_at=created_at
                    )
                    otp_manager.add_entry(entry)
            
            return otp_manager
            
        except Exception as e:
            print(f"載入失敗: {e}")
            # 嘗試從備份恢復
            backup_manager = otp_manager if 'otp_manager' in locals() else OTPManager()
            if self._restore_from_backup(backup_manager):
                return backup_manager
            return OTPManager()
    
    def _create_backup(self) -> bool:
        """
        創建備份
        
        Returns:
            bool: 是否創建成功
        """
        try:
            # 生成備份檔名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"otp_data_{timestamp}.json"
            
            # 複製檔案
            import shutil
            shutil.copy2(self.data_file, backup_file)
            
            # 清理舊備份（保留最近 10 個）
            self._cleanup_old_backups()
            
            return True
        except Exception:
            return False
    
    def _restore_from_backup(self, otp_manager: OTPManager) -> bool:
        """
        從備份恢復
        
        Args:
            otp_manager: OTP 管理器實例
            
        Returns:
            bool: 是否恢復成功
        """
        try:
            # 獲取最新的備份
            backups = sorted(self.backup_dir.glob("otp_data_*.json"), reverse=True)
            if not backups:
                return False
            
            latest_backup = backups[0]
            
            # 載入備份資料
            with open(latest_backup, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 處理資料（與 load 方法相同的邏輯）
            if isinstance(data, list):
                for item in data:
                    entry = OTPEntry(
                        label=item.get("label", "Unknown"),
                        secret=item.get("secret", ""),
                        created_at=datetime.now()
                    )
                    otp_manager.add_entry(entry)
            else:
                for item in data.get("entries", []):
                    created_at = item.get("created_at")
                    if created_at:
                        created_at = datetime.fromisoformat(created_at)
                    else:
                        created_at = datetime.now()
                    
                    entry = OTPEntry(
                        label=item.get("label", "Unknown"),
                        secret=item.get("secret", ""),
                        issuer=item.get("issuer"),
                        algorithm=item.get("algorithm", "SHA1"),
                        digits=item.get("digits", 6),
                        period=item.get("period", 30),
                        tags=item.get("tags", []),
                        created_at=created_at
                    )
                    otp_manager.add_entry(entry)
            
            return True
            
        except Exception:
            return False
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """
        清理舊備份
        
        Args:
            keep_count: 保留的備份數量
        """
        try:
            backups = sorted(self.backup_dir.glob("otp_data_*.json"))
            if len(backups) > keep_count:
                for backup in backups[:-keep_count]:
                    backup.unlink()
        except Exception:
            pass
    
    def export_json(self, otp_manager: OTPManager, file_path: str) -> bool:
        """
        導出為 JSON 檔案
        
        Args:
            otp_manager: OTP 管理器實例
            file_path: 導出檔案路徑
            
        Returns:
            bool: 是否導出成功
        """
        try:
            data = {
                "version": "2.0",
                "exported_at": datetime.now().isoformat(),
                "entries": []
            }
            
            for entry in otp_manager.get_all_entries():
                entry_data = {
                    "label": entry.label,
                    "secret": entry.secret,
                    "issuer": entry.issuer,
                    "algorithm": entry.algorithm,
                    "digits": entry.digits,
                    "period": entry.period,
                    "tags": entry.tags,
                    "uri": otp_manager.generate_uri(entry.label)
                }
                data["entries"].append(entry_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def import_json(self, file_path: str) -> Optional[OTPManager]:
        """
        從 JSON 檔案導入
        
        Args:
            file_path: 導入檔案路徑
            
        Returns:
            Optional[OTPManager]: OTP 管理器實例或 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            otp_manager = OTPManager()
            
            # 處理不同格式
            entries = data if isinstance(data, list) else data.get("entries", [])
            
            for item in entries:
                # 優先使用 URI
                if "uri" in item:
                    entry = otp_manager.parse_uri(item["uri"])
                    if entry:
                        # 更新標籤
                        if "tags" in item:
                            entry.tags = item["tags"]
                        otp_manager.add_entry(entry)
                else:
                    # 使用個別欄位
                    entry = OTPEntry(
                        label=item.get("label", "Unknown"),
                        secret=item.get("secret", ""),
                        issuer=item.get("issuer"),
                        algorithm=item.get("algorithm", "SHA1"),
                        digits=item.get("digits", 6),
                        period=item.get("period", 30),
                        tags=item.get("tags", [])
                    )
                    otp_manager.add_entry(entry)
            
            return otp_manager
            
        except Exception:
            return None
    
    def export_csv(self, otp_manager: OTPManager, file_path: str) -> bool:
        """
        導出為 CSV 檔案
        
        Args:
            otp_manager: OTP 管理器實例
            file_path: 導出檔案路徑
            
        Returns:
            bool: 是否導出成功
        """
        try:
            import csv
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["label", "secret", "issuer", "algorithm", "digits", "period", "tags"],
                    quoting=csv.QUOTE_MINIMAL
                )
                
                writer.writeheader()
                
                for entry in otp_manager.get_all_entries():
                    writer.writerow({
                        "label": entry.label,
                        "secret": entry.secret,
                        "issuer": entry.issuer or "",
                        "algorithm": entry.algorithm,
                        "digits": entry.digits,
                        "period": entry.period,
                        "tags": ";".join(entry.tags)
                    })
            
            return True
        except Exception:
            return False