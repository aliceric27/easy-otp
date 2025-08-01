"""
OTP 卡片組件
顯示單個 OTP 條目
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
from src.ui.themes.theme import theme
from src.ui.components.circular_progress import CircularProgress
from src.utils.i18n import t, add_language_observer, remove_language_observer


class OTPCard(ctk.CTkFrame):
    """OTP 卡片組件"""
    
    def __init__(self,
                 master,
                 label: str,
                 issuer: Optional[str] = None,
                 otp_code: str = "000000",
                 progress: float = 0.0,
                 period: int = 30,
                 on_copy: Optional[Callable] = None,
                 on_edit: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 **kwargs):
        """
        初始化 OTP 卡片
        
        Args:
            master: 父組件
            label: OTP 標籤
            issuer: 發行者
            otp_code: OTP 代碼
            progress: 時間進度
            period: 週期
            on_copy: 複製回調
            on_edit: 編輯回調
            on_delete: 刪除回調
        """
        # 應用卡片樣式
        card_style = theme.get_frame_style("card")
        kwargs.update(card_style)
        
        super().__init__(master, **kwargs)
        
        self.label = label
        self.issuer = issuer
        self.otp_code = otp_code
        self.progress = progress
        self.period = period
        self.on_copy = on_copy
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # 創建 UI
        self._create_widgets()
        
        # 更新顯示
        self.update_display()
        
        # 註冊語言變更觀察者（儲存參考以便清理）
        self._language_observer = self._on_language_changed
        add_language_observer(self._language_observer)
    
    def _create_widgets(self):
        """創建組件"""
        # 設定內邊距
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 主框架
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=theme.styles.padding_medium, 
                       pady=theme.styles.padding_medium, sticky="ew")
        main_frame.grid_columnconfigure(1, weight=1)
        
        # 左側：進度條
        self.progress_widget = CircularProgress(
            main_frame,
            size=50,
            thickness=4,
            progress=self.progress,
            max_value=self.period,
            command=self.on_copy
        )
        self.progress_widget.grid(row=0, column=0, rowspan=2, padx=(0, theme.styles.padding_medium))
        
        # 中間：標籤和 OTP
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)
        
        # 標籤框架
        label_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        label_frame.grid(row=0, column=0, sticky="w")
        
        # 發行者標籤
        if self.issuer:
            self.issuer_label = ctk.CTkLabel(
                label_frame,
                text=self.issuer,
                **theme.get_label_style("caption")
            )
            self.issuer_label.pack(side="left", padx=(0, theme.styles.margin_small))
        
        # 主標籤
        self.label_widget = ctk.CTkLabel(
            label_frame,
            text=self.label,
            **theme.get_label_style("normal")
        )
        self.label_widget.pack(side="left")
        
        # OTP 代碼（可點擊複製）
        self.otp_label = ctk.CTkLabel(
            info_frame,
            text=self._format_otp(self.otp_code),
            cursor="hand2",
            **theme.get_label_style("mono")
        )
        self.otp_label.grid(row=1, column=0, sticky="w", pady=(theme.styles.margin_small, 0))
        
        # 綁定點擊事件
        self.otp_label.bind("<Button-1>", lambda e: self._handle_copy())
        
        # 右側：操作按鈕
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, rowspan=2, padx=(theme.styles.padding_small, 0))
        
        # 編輯按鈕
        if self.on_edit:
            button_style = theme.get_button_style("secondary")
            self.edit_btn = ctk.CTkButton(
                button_frame,
                text=t("common.edit"),
                width=50,
                height=30,
                font=(theme.fonts.family_primary, theme.fonts.size_small),
                command=self.on_edit,
                **button_style
            )
            self.edit_btn.pack(pady=(0, theme.styles.margin_small))
        
        # 刪除按鈕
        if self.on_delete:
            button_style = theme.get_button_style("secondary")
            self.delete_btn = ctk.CTkButton(
                button_frame,
                text=t("common.delete"),
                width=50,
                height=30,
                font=(theme.fonts.family_primary, theme.fonts.size_small),
                command=self._handle_delete,
                **button_style
            )
            self.delete_btn.pack()
        
        # 複製提示
        self.copy_tooltip = None
    
    def _format_otp(self, code: str) -> str:
        """
        格式化 OTP 代碼
        
        Args:
            code: OTP 代碼
            
        Returns:
            str: 格式化後的代碼
        """
        # 在中間插入空格，例如 "123456" -> "123 456"
        if len(code) == 6:
            return f"{code[:3]} {code[3:]}"
        elif len(code) == 8:
            return f"{code[:4]} {code[4:]}"
        return code
    
    def _handle_copy(self):
        """處理複製事件"""
        if self.on_copy:
            self.on_copy()
            self._show_copy_feedback()
    
    def _handle_delete(self):
        """處理刪除事件"""
        # 顯示確認對話框
        result = tk.messagebox.askyesno(
            t("dialog.delete_otp.title"),
            t("dialog.delete_otp.message", label=self.label),
            parent=self
        )
        
        if result and self.on_delete:
            self.on_delete()
    
    def _show_copy_feedback(self):
        """顯示複製反饋"""
        # 創建臨時標籤
        if self.copy_tooltip:
            self.copy_tooltip.destroy()
        
        self.copy_tooltip = ctk.CTkLabel(
            self,
            text=t("common.copied_mark"),
            fg_color=theme.colors.success,
            corner_radius=theme.styles.radius_small,
            text_color=theme.colors.text_primary,
            font=(theme.fonts.family_primary, theme.fonts.size_small)
        )
        
        # 定位在 OTP 標籤附近
        self.copy_tooltip.place(
            in_=self.otp_label,
            relx=0.5,
            rely=-0.5,
            anchor="s"
        )
        
        # 淡出動畫
        self._fade_out_tooltip()
    
    def _fade_out_tooltip(self):
        """淡出提示標籤"""
        def fade_step(alpha: float):
            if alpha > 0 and self.copy_tooltip and self.copy_tooltip.winfo_exists():
                # 更新透明度（CustomTkinter 不支援透明度，所以直接銷毀）
                if alpha < 0.3:
                    self.copy_tooltip.destroy()
                    self.copy_tooltip = None
                else:
                    self.after(50, lambda: fade_step(alpha - 0.1))
        
        # 延遲開始淡出
        self.after(1000, lambda: fade_step(1.0))
    
    def update_display(self, otp_code: Optional[str] = None, progress: Optional[float] = None):
        """
        更新顯示
        
        Args:
            otp_code: 新的 OTP 代碼
            progress: 新的進度
        """
        if otp_code is not None:
            self.otp_code = otp_code
            self.otp_label.configure(text=self._format_otp(otp_code))
        
        if progress is not None:
            self.progress = progress
            self.progress_widget.set_progress(progress)
    
    def set_hover_effect(self, enabled: bool = True):
        """
        設定懸停效果
        
        Args:
            enabled: 是否啟用
        """
        if enabled:
            # 綁定懸停事件
            self.bind("<Enter>", lambda e: self.configure(fg_color=theme.colors.bg_hover))
            self.bind("<Leave>", lambda e: self.configure(fg_color=theme.colors.bg_secondary))
        else:
            # 解除綁定
            self.unbind("<Enter>")
            self.unbind("<Leave>")
    
    def pulse_animation(self):
        """脈衝動畫（用於更新時）"""
        self.progress_widget.pulse()
    
    def destroy(self):
        """銷毀組件"""
        # 移除語言觀察者以防止記憶體洩漏
        if hasattr(self, '_language_observer'):
            remove_language_observer(self._language_observer)
        
        # 清理提示標籤
        if self.copy_tooltip:
            self.copy_tooltip.destroy()
        
        super().destroy()