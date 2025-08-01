"""
應用程式主題設定
定義顏色、字體和樣式
"""
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class ColorScheme:
    """顏色方案"""
    # 背景顏色
    bg_primary: str = "#0e1117"      # 主背景（深黑）
    bg_secondary: str = "#1a1d24"    # 次要背景
    bg_tertiary: str = "#262a33"     # 第三層背景
    bg_hover: str = "#2d3139"        # 懸停背景
    
    # 文字顏色
    text_primary: str = "#ffffff"    # 主要文字（白色）
    text_secondary: str = "#b0b0b0"  # 次要文字（灰色）
    text_disabled: str = "#606060"   # 禁用文字
    
    # 強調色
    accent_primary: str = "#3b82f6"  # 主要強調色（藍色）
    accent_hover: str = "#2563eb"    # 強調色懸停
    accent_pressed: str = "#1d4ed8"  # 強調色按下
    
    # 狀態顏色
    success: str = "#10b981"         # 成功（綠色）
    warning: str = "#f59e0b"         # 警告（橘色）
    error: str = "#ef4444"           # 錯誤（紅色）
    info: str = "#3b82f6"            # 資訊（藍色）
    
    # OTP 進度顏色
    progress_full: str = "#10b981"   # 進度滿（綠色）
    progress_mid: str = "#f59e0b"    # 進度中（橘色）
    progress_low: str = "#ef4444"    # 進度低（紅色）
    
    # 邊框和分隔線
    border: str = "#2d3139"          # 邊框顏色
    divider: str = "#1a1d24"         # 分隔線顏色


@dataclass
class FontScheme:
    """字體方案"""
    # 字體家族
    family_primary: str = "Segoe UI"
    family_mono: str = "Consolas"
    
    # 字體大小
    size_small: int = 11
    size_normal: int = 13
    size_medium: int = 15
    size_large: int = 18
    size_xlarge: int = 24
    size_xxlarge: int = 32
    
    # 字體粗細
    weight_normal: str = "normal"
    weight_medium: str = "normal"  # Tkinter 不支援 500，使用 normal
    weight_bold: str = "bold"


@dataclass
class StyleScheme:
    """樣式方案"""
    # 圓角半徑
    radius_small: int = 4
    radius_medium: int = 8
    radius_large: int = 12
    radius_xlarge: int = 16
    
    # 內邊距
    padding_small: int = 8
    padding_medium: int = 12
    padding_large: int = 16
    padding_xlarge: int = 20
    
    # 外邊距
    margin_small: int = 4
    margin_medium: int = 8
    margin_large: int = 12
    margin_xlarge: int = 16
    
    # 按鈕高度
    button_height_small: int = 32
    button_height_medium: int = 40
    button_height_large: int = 48
    
    # 動畫時長（毫秒）
    animation_fast: int = 100
    animation_normal: int = 200
    animation_slow: int = 300


class Theme:
    """主題管理器"""
    
    def __init__(self):
        self.colors = ColorScheme()
        self.fonts = FontScheme()
        self.styles = StyleScheme()
    
    def get_button_style(self, variant: str = "primary") -> Dict:
        """
        獲取按鈕樣式
        
        Args:
            variant: 按鈕變體（primary, secondary, danger, success）
            
        Returns:
            Dict: CustomTkinter 按鈕樣式
        """
        base_style = {
            "corner_radius": self.styles.radius_medium,
            "anchor": "center",
            "compound": "left"
        }
        
        if variant == "primary":
            base_style.update({
                "fg_color": self.colors.accent_primary,
                "hover_color": self.colors.accent_hover,
                "text_color": self.colors.text_primary,
                "border_width": 0
            })
        elif variant == "secondary":
            base_style.update({
                "fg_color": self.colors.bg_secondary,
                "hover_color": self.colors.bg_hover,
                "text_color": self.colors.text_primary,
                "border_width": 1,
                "border_color": self.colors.border
            })
        elif variant == "danger":
            base_style.update({
                "fg_color": self.colors.error,
                "hover_color": "#dc2626",
                "text_color": self.colors.text_primary,
                "border_width": 0
            })
        elif variant == "success":
            base_style.update({
                "fg_color": self.colors.success,
                "hover_color": "#059669",
                "text_color": self.colors.text_primary,
                "border_width": 0
            })
        
        return base_style
    
    def get_entry_style(self) -> Dict:
        """
        獲取輸入框樣式
        
        Returns:
            Dict: CustomTkinter 輸入框樣式
        """
        return {
            "corner_radius": self.styles.radius_medium,
            "font": (self.fonts.family_primary, self.fonts.size_normal),
            "fg_color": self.colors.bg_secondary,
            "border_color": self.colors.border,
            "border_width": 1,
            "text_color": self.colors.text_primary,
            "placeholder_text_color": self.colors.text_disabled
        }
    
    def get_frame_style(self, variant: str = "primary") -> Dict:
        """
        獲取框架樣式
        
        Args:
            variant: 框架變體（primary, secondary, card）
            
        Returns:
            Dict: CustomTkinter 框架樣式
        """
        if variant == "primary":
            return {
                "corner_radius": 0,
                "fg_color": self.colors.bg_primary,
                "border_width": 0
            }
        elif variant == "secondary":
            return {
                "corner_radius": 0,
                "fg_color": self.colors.bg_secondary,
                "border_width": 0
            }
        elif variant == "card":
            return {
                "corner_radius": self.styles.radius_large,
                "fg_color": self.colors.bg_secondary,
                "border_width": 1,
                "border_color": self.colors.border
            }
        
        return {}
    
    def get_label_style(self, variant: str = "normal") -> Dict:
        """
        獲取標籤樣式
        
        Args:
            variant: 標籤變體（normal, heading, caption, mono）
            
        Returns:
            Dict: CustomTkinter 標籤樣式
        """
        base_style = {
            "text_color": self.colors.text_primary,
            "anchor": "w",
            "compound": "left"
        }
        
        if variant == "normal":
            base_style["font"] = (self.fonts.family_primary, self.fonts.size_normal)
        elif variant == "heading":
            base_style["font"] = (self.fonts.family_primary, self.fonts.size_xlarge, self.fonts.weight_bold)
        elif variant == "caption":
            base_style["font"] = (self.fonts.family_primary, self.fonts.size_small)
            base_style["text_color"] = self.colors.text_secondary
        elif variant == "mono":
            base_style["font"] = (self.fonts.family_mono, self.fonts.size_xlarge, self.fonts.weight_bold)
        
        return base_style
    
    def get_progress_color(self, progress: float) -> str:
        """
        根據進度獲取顏色
        
        Args:
            progress: 進度值（0.0 到 1.0）
            
        Returns:
            str: 顏色值
        """
        if progress < 0.33:
            return self.colors.progress_full
        elif progress < 0.67:
            return self.colors.progress_mid
        else:
            return self.colors.progress_low
    
    def interpolate_color(self, color1: str, color2: str, progress: float) -> str:
        """
        在兩個顏色之間插值
        
        Args:
            color1: 起始顏色
            color2: 結束顏色
            progress: 進度（0.0 到 1.0）
            
        Returns:
            str: 插值後的顏色
        """
        # 將十六進制顏色轉換為 RGB
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # 將 RGB 轉換為十六進制顏色
        def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
            return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
        # 轉換顏色
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # 插值
        rgb = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * progress) for i in range(3))
        
        return rgb_to_hex(rgb)


# 全域主題實例
theme = Theme()