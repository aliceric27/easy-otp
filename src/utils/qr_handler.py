"""
QR Code 處理工具
處理 QR Code 的讀取和生成
"""
import io
from typing import Optional, List, Tuple
from PIL import Image
from pyzbar.pyzbar import decode
import qrcode
from pathlib import Path


class QRHandler:
    """QR Code 處理器"""
    
    @staticmethod
    def read_qr_from_image(image_path: str) -> Optional[str]:
        """
        從圖片讀取 QR Code
        
        Args:
            image_path: 圖片路徑
            
        Returns:
            Optional[str]: QR Code 內容或 None
        """
        try:
            # 開啟圖片
            image = Image.open(image_path)
            
            # 如果是 RGBA，轉換為 RGB
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            # 解碼 QR Code
            decoded_objects = decode(image)
            
            if decoded_objects:
                # 返回第一個 QR Code 的內容
                return decoded_objects[0].data.decode('utf-8')
            
            return None
            
        except Exception as e:
            print(f"讀取 QR Code 失敗: {e}")
            return None
    
    @staticmethod
    def read_multiple_qr_from_image(image_path: str) -> List[str]:
        """
        從圖片讀取多個 QR Code
        
        Args:
            image_path: 圖片路徑
            
        Returns:
            List[str]: QR Code 內容列表
        """
        results = []
        
        try:
            # 開啟圖片
            image = Image.open(image_path)
            
            # 如果是 RGBA，轉換為 RGB
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            # 解碼所有 QR Code
            decoded_objects = decode(image)
            
            for obj in decoded_objects:
                try:
                    content = obj.data.decode('utf-8')
                    results.append(content)
                except Exception:
                    continue
            
        except Exception as e:
            print(f"讀取 QR Code 失敗: {e}")
        
        return results
    
    @staticmethod
    def generate_qr_code(data: str, size: Tuple[int, int] = (300, 300)) -> Image.Image:
        """
        生成 QR Code 圖片
        
        Args:
            data: QR Code 資料
            size: 圖片大小
            
        Returns:
            Image.Image: QR Code 圖片
        """
        # 創建 QR Code
        qr = qrcode.QRCode(
            version=None,  # 自動調整版本
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # 生成圖片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 調整大小
        if img.size != size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        
        return img
    
    @staticmethod
    def save_qr_code(data: str, output_path: str, size: Tuple[int, int] = (300, 300)) -> bool:
        """
        生成並儲存 QR Code
        
        Args:
            data: QR Code 資料
            output_path: 輸出路徑
            size: 圖片大小
            
        Returns:
            bool: 是否儲存成功
        """
        try:
            img = QRHandler.generate_qr_code(data, size)
            img.save(output_path)
            return True
        except Exception as e:
            print(f"儲存 QR Code 失敗: {e}")
            return False
    
    @staticmethod
    def generate_qr_with_logo(data: str, logo_path: str, size: Tuple[int, int] = (300, 300)) -> Optional[Image.Image]:
        """
        生成帶 Logo 的 QR Code
        
        Args:
            data: QR Code 資料
            logo_path: Logo 圖片路徑
            size: 圖片大小
            
        Returns:
            Optional[Image.Image]: QR Code 圖片或 None
        """
        try:
            # 生成基本 QR Code
            qr_img = QRHandler.generate_qr_code(data, size)
            
            # 載入 Logo
            logo = Image.open(logo_path)
            
            # 計算 Logo 大小（QR Code 的 1/5）
            qr_width, qr_height = qr_img.size
            logo_size = min(qr_width, qr_height) // 5
            
            # 調整 Logo 大小
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # 如果 Logo 有透明通道，創建白色背景
            if logo.mode == 'RGBA':
                background = Image.new('RGB', (logo_size, logo_size), (255, 255, 255))
                background.paste(logo, mask=logo.split()[3])
                logo = background
            
            # 計算 Logo 位置（居中）
            logo_x = (qr_width - logo_size) // 2
            logo_y = (qr_height - logo_size) // 2
            
            # 將 Logo 貼到 QR Code 上
            qr_img.paste(logo, (logo_x, logo_y))
            
            return qr_img
            
        except Exception as e:
            print(f"生成帶 Logo 的 QR Code 失敗: {e}")
            return None
    
    @staticmethod
    def batch_save_qr_codes(data_dict: dict, output_dir: str, size: Tuple[int, int] = (300, 300)) -> dict:
        """
        批量生成並儲存 QR Code
        
        Args:
            data_dict: {檔名: QR Code 資料} 字典
            output_dir: 輸出目錄
            size: 圖片大小
            
        Returns:
            dict: {檔名: 是否成功} 字典
        """
        results = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for filename, data in data_dict.items():
            # 確保檔名有 .png 副檔名
            if not filename.endswith('.png'):
                filename += '.png'
            
            # 生成完整路徑
            file_path = output_path / filename
            
            # 儲存 QR Code
            success = QRHandler.save_qr_code(data, str(file_path), size)
            results[filename] = success
        
        return results
    
    @staticmethod
    def is_valid_otp_uri(data: str) -> bool:
        """
        檢查是否為有效的 OTP URI
        
        Args:
            data: URI 字串
            
        Returns:
            bool: 是否為有效的 OTP URI
        """
        if not data:
            return False
        
        # OTP URI 應該以 otpauth:// 開頭
        return data.startswith('otpauth://totp/') or data.startswith('otpauth://hotp/')

    @staticmethod
    def is_valid_google_otp_uri(data: str) -> bool:
        """
        檢查是否為 Google Authenticator 匯出 QR Code 的 otpauth-migration URI
        """
        return data.startswith("otpauth-migration://offline?data=")

    @staticmethod
    def extract_otp_info(uri: str) -> Optional[dict]:
        """
        從 OTP URI 提取資訊
        
        Args:
            uri: OTP URI
            
        Returns:
            Optional[dict]: OTP 資訊或 None
        """
        if not QRHandler.is_valid_otp_uri(uri):
            return None
        
        try:
            # 簡單解析 URI
            # 格式: otpauth://totp/LABEL?secret=SECRET&issuer=ISSUER
            import urllib.parse
            
            # 解析 URL
            parsed = urllib.parse.urlparse(uri)
            
            # 提取標籤
            label = urllib.parse.unquote(parsed.path.strip('/'))
            
            # 解析查詢參數
            params = urllib.parse.parse_qs(parsed.query)
            
            return {
                'type': parsed.hostname,  # totp 或 hotp
                'label': label,
                'secret': params.get('secret', [''])[0],
                'issuer': params.get('issuer', [''])[0],
                'algorithm': params.get('algorithm', ['SHA1'])[0],
                'digits': int(params.get('digits', ['6'])[0]),
                'period': int(params.get('period', ['30'])[0])
            }
            
        except Exception:
            return None