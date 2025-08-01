"""
空狀態組件
當沒有 OTP 條目時顯示
"""
import customtkinter as ctk
from typing import Optional, Callable
from src.ui.themes.theme import theme


class EmptyState(ctk.CTkFrame):
    """空狀態組件"""
    
    def __init__(self,
                 master,
                 title: str = "還沒有任何 OTP",
                 description: str = "點擊下方按鈕開始新增",
                 icon: str = "🔐",
                 action_text: str = "新增第一個 OTP",
                 on_action: Optional[Callable] = None,
                 **kwargs):
        """
        初始化空狀態
        
        Args:
            master: 父組件
            title: 標題
            description: 描述
            icon: 圖標
            action_text: 操作按鈕文字
            on_action: 操作回調
        """
        kwargs['fg_color'] = "transparent"
        super().__init__(master, **kwargs)
        
        self.title = title
        self.description = description
        self.icon = icon
        self.action_text = action_text
        self.on_action = on_action
        
        # 創建組件
        self._create_widgets()
    
    def _create_widgets(self):
        """創建組件"""
        # 容器（居中）
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # 圖標 - 使用文字替代
        if self.icon and self.icon != "🔐":
            icon_label = ctk.CTkLabel(
                container,
                text=self.icon,
                font=(theme.fonts.family_primary, 48),
                text_color=theme.colors.text_secondary
            )
            icon_label.pack(pady=(0, theme.styles.padding_large))
        else:
            # 使用 OTP 文字作為圖標
            icon_label = ctk.CTkLabel(
                container,
                text="OTP",
                font=(theme.fonts.family_primary, 48, theme.fonts.weight_bold),
                text_color=theme.colors.accent_primary
            )
            icon_label.pack(pady=(0, theme.styles.padding_large))
        
        # 標題
        title_label = ctk.CTkLabel(
            container,
            text=self.title,
            font=(theme.fonts.family_primary, theme.fonts.size_large, theme.fonts.weight_bold),
            text_color=theme.colors.text_primary
        )
        title_label.pack(pady=(0, theme.styles.padding_small))
        
        # 描述
        desc_label = ctk.CTkLabel(
            container,
            text=self.description,
            font=(theme.fonts.family_primary, theme.fonts.size_normal),
            text_color=theme.colors.text_secondary
        )
        desc_label.pack(pady=(0, theme.styles.padding_large))
        
        # 操作按鈕
        if self.on_action:
            action_btn = ctk.CTkButton(
                container,
                text=self.action_text,
                command=self.on_action,
                width=200,
                **theme.get_button_style("primary")
            )
            action_btn.pack()
    
    def update_content(self, 
                      title: Optional[str] = None,
                      description: Optional[str] = None,
                      icon: Optional[str] = None):
        """
        更新內容
        
        Args:
            title: 新標題
            description: 新描述
            icon: 新圖標
        """
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if icon is not None:
            self.icon = icon
        
        # 重新創建組件
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()