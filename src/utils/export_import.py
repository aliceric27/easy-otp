"""
導出導入工具
處理 OTP 資料的導出和導入功能
"""
import os
import sys
import json
from typing import List, Optional, Dict
from pathlib import Path

# 處理模組導入
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.otp_manager import OTPManager, OTPEntry
from src.core.storage import StorageManager
from src.utils.qr_handler import QRHandler
from src.utils.otpauth_migration import otpauth_migration_decoder


class ExportImportManager:
    """導出導入管理器"""
    
    def __init__(self, storage_manager: StorageManager):
        """
        初始化導出導入管理器
        
        Args:
            storage_manager: 儲存管理器實例
        """
        self.storage_manager = storage_manager
        self.qr_handler = QRHandler()
    
    def export_to_qr_codes(self, otp_manager: OTPManager, output_dir: str, 
                          size: tuple = (300, 300)) -> Dict[str, bool]:
        """
        導出所有 OTP 為 QR Code 圖片
        
        Args:
            otp_manager: OTP 管理器實例
            output_dir: 輸出目錄
            size: QR Code 大小
            
        Returns:
            Dict[str, bool]: {檔名: 是否成功} 字典
        """
        # 準備導出資料
        data_dict = {}
        
        for entry in otp_manager.get_all_entries():
            # 生成 URI
            uri = otp_manager.generate_uri(entry.label)
            if uri:
                # 使用安全的檔名
                safe_filename = self._make_safe_filename(entry.label)
                data_dict[safe_filename] = uri
        
        # 批量生成 QR Code
        return self.qr_handler.batch_save_qr_codes(data_dict, output_dir, size)
    
    def export_single_qr(self, otp_manager: OTPManager, label: str, 
                        output_path: str, size: tuple = (300, 300)) -> bool:
        """
        導出單個 OTP 為 QR Code
        
        Args:
            otp_manager: OTP 管理器實例
            label: OTP 標籤
            output_path: 輸出路徑
            size: QR Code 大小
            
        Returns:
            bool: 是否成功
        """
        # 生成 URI
        uri = otp_manager.generate_uri(label)
        if not uri:
            return False
        
        # 儲存 QR Code
        return self.qr_handler.save_qr_code(uri, output_path, size)
    
    def import_from_qr_image(self, otp_manager: OTPManager, image_path: str) -> List[str]:
        """
        從 QR Code 圖片導入 OTP
        
        Args:
            otp_manager: OTP 管理器實例
            image_path: 圖片路徑
            
        Returns:
            List[str]: 成功導入的標籤列表
        """
        imported_labels = []
        
        # 讀取所有 QR Code
        qr_contents = self.qr_handler.read_multiple_qr_from_image(image_path)
        
        for content in qr_contents:
            uris = []
            # 檢查是否為 OTP URI
            if self.qr_handler.is_valid_google_otp_uri(content):
                uris = otpauth_migration_decoder.parse_migration_uri(content)
            elif self.qr_handler.is_valid_otp_uri(content):
                uris = [content]

            for uri in uris:
                if self.qr_handler.is_valid_otp_uri(uri):
                    entry = otp_manager.parse_uri(uri)
                    if entry:
                        # 檢查是否已存在
                        if entry.label in otp_manager.entries:
                            # 生成新標籤
                            base_label = entry.label
                            counter = 1
                            while f"{base_label} ({counter})" in otp_manager.entries:
                                counter += 1
                            entry.label = f"{base_label} ({counter})"

                        # 新增條目
                        if otp_manager.add_entry(entry):
                            imported_labels.append(entry.label)
        
        return imported_labels
    
    def import_from_qr_directory(self, otp_manager: OTPManager, directory: str) -> Dict[str, List[str]]:
        """
        從目錄中的所有 QR Code 圖片導入
        
        Args:
            otp_manager: OTP 管理器實例
            directory: 目錄路徑
            
        Returns:
            Dict[str, List[str]]: {檔名: [成功導入的標籤]} 字典
        """
        results = {}
        dir_path = Path(directory)
        
        # 支援的圖片格式
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        
        # 遍歷所有圖片檔案
        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                # 導入單個檔案
                imported = self.import_from_qr_image(otp_manager, str(file_path))
                if imported:
                    results[file_path.name] = imported
        
        return results
    
    def export_to_google_auth_format(self, otp_manager: OTPManager, output_path: str) -> bool:
        """
        導出為 Google Authenticator 相容格式
        
        Args:
            otp_manager: OTP 管理器實例
            output_path: 輸出路徑
            
        Returns:
            bool: 是否成功
        """
        try:
            # 準備導出資料
            export_data = []
            
            for entry in otp_manager.get_all_entries():
                # 生成 URI
                uri = otp_manager.generate_uri(entry.label)
                if uri:
                    export_data.append({
                        "uri": uri,
                        "label": entry.label,
                        "issuer": entry.issuer
                    })
            
            # 寫入檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in export_data:
                    f.write(f"{item['uri']}\n")
            
            return True
            
        except Exception:
            return False
    
    def import_from_google_auth_format(self, otp_manager: OTPManager, file_path: str) -> List[str]:
        """
        從 Google Authenticator 格式檔案導入
        
        Args:
            otp_manager: OTP 管理器實例
            file_path: 檔案路徑
            
        Returns:
            List[str]: 成功導入的標籤列表
        """
        imported_labels = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and self.qr_handler.is_valid_otp_uri(line):
                    # 解析 URI
                    entry = otp_manager.parse_uri(line)
                    if entry:
                        # 處理重複標籤
                        if entry.label in otp_manager.entries:
                            base_label = entry.label
                            counter = 1
                            while f"{base_label} ({counter})" in otp_manager.entries:
                                counter += 1
                            entry.label = f"{base_label} ({counter})"
                        
                        # 新增條目
                        if otp_manager.add_entry(entry):
                            imported_labels.append(entry.label)
            
        except Exception:
            pass
        
        return imported_labels
    
    def _make_safe_filename(self, name: str) -> str:
        """
        生成安全的檔名
        
        Args:
            name: 原始名稱
            
        Returns:
            str: 安全的檔名
        """
        # 移除或替換不安全的字元
        unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        safe_name = name
        
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # 限制長度
        if len(safe_name) > 200:
            safe_name = safe_name[:200]
        
        # 確保不為空
        if not safe_name:
            safe_name = "unnamed"
        
        return safe_name
    
    def create_backup(self, otp_manager: OTPManager, backup_name: Optional[str] = None) -> Optional[str]:
        """
        創建完整備份（包含 JSON 和 QR Codes）
        
        Args:
            otp_manager: OTP 管理器實例
            backup_name: 備份名稱（可選）
            
        Returns:
            Optional[str]: 備份目錄路徑或 None
        """
        try:
            # 生成備份目錄名稱
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if backup_name:
                backup_dir_name = f"{backup_name}_{timestamp}"
            else:
                backup_dir_name = f"backup_{timestamp}"
            
            # 創建備份目錄
            backup_path = self.storage_manager.data_dir / "exports" / backup_dir_name
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 導出 JSON
            json_path = backup_path / "otp_data.json"
            if not self.storage_manager.export_json(otp_manager, str(json_path)):
                return None
            
            # 導出 CSV
            csv_path = backup_path / "otp_data.csv"
            self.storage_manager.export_csv(otp_manager, str(csv_path))
            
            # 導出 QR Codes
            qr_path = backup_path / "qr_codes"
            self.export_to_qr_codes(otp_manager, str(qr_path))
            
            # 創建備份資訊檔案
            info_path = backup_path / "backup_info.txt"
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(f"Easy OTP Backup\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total entries: {len(otp_manager.entries)}\n")
                f.write(f"\nContents:\n")
                f.write(f"- otp_data.json: Complete data in JSON format\n")
                f.write(f"- otp_data.csv: Data in CSV format\n")
                f.write(f"- qr_codes/: Individual QR codes for each entry\n")
            
            return str(backup_path)
            
        except Exception:
            return None