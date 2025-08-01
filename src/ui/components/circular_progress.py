"""
圓形進度條組件
用於顯示 OTP 倒數計時
"""
import tkinter as tk
import customtkinter as ctk
import math
from typing import Optional, Callable
from src.ui.themes.theme import theme


class CircularProgress(ctk.CTkCanvas):
    """圓形進度條組件"""
    
    def __init__(self, 
                 master, 
                 size: int = 60,
                 thickness: int = 6,
                 progress: float = 0.0,
                 show_text: bool = True,
                 text_format: str = "{:.0f}s",
                 max_value: int = 30,
                 command: Optional[Callable] = None,
                 **kwargs):
        """
        初始化圓形進度條
        
        Args:
            master: 父組件
            size: 進度條大小（直徑）
            thickness: 進度條厚度
            progress: 初始進度（0.0 到 1.0）
            show_text: 是否顯示文字
            text_format: 文字格式
            max_value: 最大值（用於計算顯示文字）
            command: 點擊回調函數
        """
        # 設定畫布大小
        kwargs['width'] = size
        kwargs['height'] = size
        kwargs['highlightthickness'] = 0
        kwargs['bg'] = theme.colors.bg_primary
        
        super().__init__(master, **kwargs)
        
        self.size = size
        self.thickness = thickness
        self.progress = progress
        self.show_text = show_text
        self.text_format = text_format
        self.max_value = max_value
        self.command = command
        
        # 計算參數
        self.center = size // 2
        self.radius = (size - thickness) // 2
        
        # 繪製元素 ID
        self.bg_arc_id = None
        self.progress_arc_id = None
        self.text_id = None
        
        # 綁定事件
        if command:
            self.bind("<Button-1>", lambda e: command())
            self.configure(cursor="hand2")
        
        # 初始繪製
        self.draw()
    
    def draw(self):
        """繪製進度條"""
        # 清除畫布
        self.delete("all")
        
        # 繪製背景圓弧
        self.bg_arc_id = self.create_arc(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            start=90,
            extent=-360,
            outline=theme.colors.bg_tertiary,
            width=self.thickness,
            style=tk.ARC
        )
        
        # 計算進度角度
        extent = -360 * self.progress
        
        # 獲取進度顏色
        color = theme.get_progress_color(self.progress)
        
        # 繪製進度圓弧
        if self.progress > 0:
            self.progress_arc_id = self.create_arc(
                self.center - self.radius,
                self.center - self.radius,
                self.center + self.radius,
                self.center + self.radius,
                start=90,
                extent=extent,
                outline=color,
                width=self.thickness,
                style=tk.ARC
            )
        
        # 繪製文字
        if self.show_text:
            # 計算剩餘時間
            remaining = self.max_value * (1 - self.progress)
            text = self.text_format.format(remaining)
            
            self.text_id = self.create_text(
                self.center,
                self.center,
                text=text,
                fill=theme.colors.text_primary,
                font=(theme.fonts.family_primary, 
                      self.size // 4, 
                      theme.fonts.weight_medium)
            )
    
    def set_progress(self, progress: float):
        """
        設定進度
        
        Args:
            progress: 進度值（0.0 到 1.0）
        """
        self.progress = max(0.0, min(1.0, progress))
        self.draw()
    
    def set_max_value(self, max_value: int):
        """
        設定最大值
        
        Args:
            max_value: 最大值
        """
        self.max_value = max_value
        self.draw()
    
    def animate_to(self, target_progress: float, duration: int = 200, steps: int = 20):
        """
        動畫過渡到目標進度
        
        Args:
            target_progress: 目標進度
            duration: 動畫持續時間（毫秒）
            steps: 動畫步數
        """
        start_progress = self.progress
        progress_diff = target_progress - start_progress
        step_duration = duration // steps
        
        def animate_step(step: int):
            if step <= steps:
                # 計算當前進度
                progress = start_progress + (progress_diff * step / steps)
                self.set_progress(progress)
                
                # 繼續下一步
                self.after(step_duration, lambda: animate_step(step + 1))
        
        animate_step(1)
    
    def pulse(self, duration: int = 300):
        """
        脈衝動畫效果
        
        Args:
            duration: 動畫持續時間
        """
        # 保存原始大小
        original_scale = 1.0
        target_scale = 1.1
        steps = 10
        step_duration = duration // (steps * 2)
        
        def scale_step(step: int, expanding: bool):
            if expanding and step <= steps:
                # 放大階段
                scale = original_scale + (target_scale - original_scale) * step / steps
                self._apply_scale(scale)
                self.after(step_duration, lambda: scale_step(step + 1, True))
            elif not expanding and step > 0:
                # 縮小階段
                scale = original_scale + (target_scale - original_scale) * step / steps
                self._apply_scale(scale)
                self.after(step_duration, lambda: scale_step(step - 1, False))
            elif expanding:
                # 開始縮小
                scale_step(steps, False)
        
        scale_step(1, True)
    
    def _apply_scale(self, scale: float):
        """
        應用縮放
        
        Args:
            scale: 縮放比例
        """
        # 計算新的參數
        new_radius = int(self.radius * scale)
        new_center = self.size // 2
        
        # 更新圓弧
        for arc_id in [self.bg_arc_id, self.progress_arc_id]:
            if arc_id:
                self.coords(
                    arc_id,
                    new_center - new_radius,
                    new_center - new_radius,
                    new_center + new_radius,
                    new_center + new_radius
                )
    
    def configure(self, **kwargs):
        """配置組件"""
        # 處理自定義屬性
        if 'progress' in kwargs:
            self.set_progress(kwargs.pop('progress'))
        if 'max_value' in kwargs:
            self.set_max_value(kwargs.pop('max_value'))
        if 'show_text' in kwargs:
            self.show_text = kwargs.pop('show_text')
            self.draw()
        if 'text_format' in kwargs:
            self.text_format = kwargs.pop('text_format')
            self.draw()
        
        # 處理其他屬性
        super().configure(**kwargs)