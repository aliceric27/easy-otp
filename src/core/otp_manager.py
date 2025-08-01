"""
OTP 管理核心模組
處理 OTP 的生成、驗證和時間計算
"""
import pyotp
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OTPEntry:
    """OTP 條目資料類別"""
    label: str
    secret: str
    issuer: Optional[str] = None
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30
    tags: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()


class OTPManager:
    """OTP 管理器"""
    
    def __init__(self):
        self.entries: Dict[str, OTPEntry] = {}
    
    def add_entry(self, entry: OTPEntry) -> bool:
        """
        新增新的 OTP 條目
        
        Args:
            entry: OTP 條目
            
        Returns:
            bool: 是否新增成功
        """
        if entry.label in self.entries:
            return False
        
        # 驗證 secret 是否有效
        try:
            totp = pyotp.TOTP(entry.secret)
            totp.now()  # 嘗試生成 OTP
        except Exception:
            return False
        
        self.entries[entry.label] = entry
        return True
    
    def remove_entry(self, label: str) -> bool:
        """
        移除 OTP 條目
        
        Args:
            label: 條目標籤
            
        Returns:
            bool: 是否移除成功
        """
        if label in self.entries:
            del self.entries[label]
            return True
        return False
    
    def update_entry(self, old_label: str, new_entry: OTPEntry) -> bool:
        """
        更新 OTP 條目
        
        Args:
            old_label: 舊標籤
            new_entry: 新條目資料
            
        Returns:
            bool: 是否更新成功
        """
        if old_label not in self.entries:
            return False
        
        # 如果標籤改變，檢查新標籤是否已存在
        if old_label != new_entry.label and new_entry.label in self.entries:
            return False
        
        # 驗證新的 secret
        try:
            totp = pyotp.TOTP(new_entry.secret)
            totp.now()
        except Exception:
            return False
        
        # 移除舊條目並新增新條目
        del self.entries[old_label]
        self.entries[new_entry.label] = new_entry
        return True
    
    def get_entry(self, label: str) -> Optional[OTPEntry]:
        """
        獲取 OTP 條目
        
        Args:
            label: 條目標籤
            
        Returns:
            Optional[OTPEntry]: OTP 條目或 None
        """
        return self.entries.get(label)
    
    def get_all_entries(self) -> List[OTPEntry]:
        """
        獲取所有 OTP 條目
        
        Returns:
            List[OTPEntry]: 所有 OTP 條目列表
        """
        return list(self.entries.values())
    
    def generate_otp(self, label: str) -> Optional[str]:
        """
        生成指定條目的當前 OTP
        
        Args:
            label: 條目標籤
            
        Returns:
            Optional[str]: OTP 碼或 None
        """
        entry = self.entries.get(label)
        if not entry:
            return None
        
        try:
            totp = pyotp.TOTP(
                entry.secret,
                digits=entry.digits,
                interval=entry.period
            )
            return totp.now()
        except Exception:
            return None
    
    def get_otp_with_remaining_time(self, label: str) -> Optional[Tuple[str, int]]:
        """
        獲取 OTP 和剩餘時間
        
        Args:
            label: 條目標籤
            
        Returns:
            Optional[Tuple[str, int]]: (OTP碼, 剩餘秒數) 或 None
        """
        entry = self.entries.get(label)
        if not entry:
            return None
        
        try:
            totp = pyotp.TOTP(
                entry.secret,
                digits=entry.digits,
                interval=entry.period
            )
            otp = totp.now()
            remaining = entry.period - (int(time.time()) % entry.period)
            return otp, remaining
        except Exception:
            return None
    
    def get_progress(self, label: str) -> float:
        """
        獲取 OTP 時間進度（0.0 到 1.0）
        
        Args:
            label: 條目標籤
            
        Returns:
            float: 進度百分比
        """
        entry = self.entries.get(label)
        if not entry:
            return 0.0
        
        elapsed = int(time.time()) % entry.period
        return elapsed / entry.period
    
    def parse_uri(self, uri: str) -> Optional[OTPEntry]:
        """
        解析 OTP URI
        
        Args:
            uri: OTP URI 字串
            
        Returns:
            Optional[OTPEntry]: OTP 條目或 None
        """
        try:
            totp = pyotp.parse_uri(uri)
            
            # 提取標籤和發行者
            label = totp.name or "Unknown"
            issuer = totp.issuer
            
            # 如果標籤包含發行者資訊，嘗試分離
            if not issuer and ":" in label:
                parts = label.split(":", 1)
                issuer = parts[0]
                label = parts[1]
            
            return OTPEntry(
                label=label,
                secret=totp.secret,
                issuer=issuer,
                digits=totp.digits,
                period=totp.interval
            )
        except Exception:
            return None
    
    def generate_uri(self, label: str) -> Optional[str]:
        """
        生成 OTP URI
        
        Args:
            label: 條目標籤
            
        Returns:
            Optional[str]: OTP URI 或 None
        """
        entry = self.entries.get(label)
        if not entry:
            return None
        
        try:
            totp = pyotp.TOTP(
                entry.secret,
                digits=entry.digits,
                interval=entry.period
            )
            
            # 組合名稱
            name = entry.label
            if entry.issuer:
                name = f"{entry.issuer}:{entry.label}"
            
            return totp.provisioning_uri(
                name=name,
                issuer_name=entry.issuer
            )
        except Exception:
            return None
    
    def filter_by_tags(self, tags: List[str]) -> List[OTPEntry]:
        """
        根據標籤篩選條目
        
        Args:
            tags: 標籤列表
            
        Returns:
            List[OTPEntry]: 符合的條目列表
        """
        if not tags:
            return self.get_all_entries()
        
        filtered = []
        for entry in self.entries.values():
            if any(tag in entry.tags for tag in tags):
                filtered.append(entry)
        
        return filtered
    
    def search_entries(self, query: str) -> List[OTPEntry]:
        """
        搜尋條目
        
        Args:
            query: 搜尋關鍵字
            
        Returns:
            List[OTPEntry]: 符合的條目列表
        """
        query = query.lower()
        results = []
        
        for entry in self.entries.values():
            # 搜尋標籤、發行者和標籤
            if (query in entry.label.lower() or
                (entry.issuer and query in entry.issuer.lower()) or
                any(query in tag.lower() for tag in entry.tags)):
                results.append(entry)
        
        return results