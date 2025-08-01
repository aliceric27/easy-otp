"""
搜尋框組件
提供即時搜尋功能
"""
import customtkinter as ctk
from typing import Optional, Callable
from src.ui.themes.theme import theme
from src.utils.i18n import t, add_language_observer, remove_language_observer


class SearchBar(ctk.CTkFrame):
    """搜尋框組件"""
    
    def __init__(self,
                 master,
                 placeholder: str = "搜尋 OTP...",
                 on_search: Optional[Callable[[str], None]] = None,
                 **kwargs):
        """
        初始化搜尋框
        
        Args:
            master: 父組件
            placeholder: 佔位符文字
            on_search: 搜尋回調函數
        """
        # 設定框架樣式
        kwargs['fg_color'] = "transparent"
        super().__init__(master, **kwargs)
        
        self.on_search = on_search
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        
        # 創建組件
        self._create_widgets(placeholder)
        
        # 註冊語言變更觀察者
        self._language_observer = self._on_language_changed
        add_language_observer(self._language_observer)
    
    def _create_widgets(self, placeholder: str):
        """創建組件"""
        # 搜尋圖標
        self.search_icon = ctk.CTkLabel(
            self,
            text=t("common.search_colon"),
            font=(theme.fonts.family_primary, theme.fonts.size_normal),
            text_color=theme.colors.text_secondary
        )
        self.search_icon.pack(side="left", padx=(theme.styles.padding_small, 0))
        
        # 搜尋輸入框
        entry_style = theme.get_entry_style()
        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text=placeholder,
            **entry_style
        )
        self.search_entry.pack(
            side="left", 
            fill="x", 
            expand=True, 
            padx=theme.styles.padding_small
        )
        
        # 清除按鈕（初始隱藏）
        button_style = theme.get_button_style("secondary")
        self.clear_btn = ctk.CTkButton(
            self,
            text="×",
            width=40,
            height=30,
            font=(theme.fonts.family_primary, theme.fonts.size_large),
            command=self.clear,
            **button_style
        )
        
        # 綁定快捷鍵
        self.search_entry.bind("<Escape>", lambda e: self.clear())
        self.search_entry.bind("<Control-f>", lambda e: self.focus())
    
    def _on_search_changed(self, *args):
        """搜尋內容改變時的回調"""
        query = self.search_var.get()
        
        # 顯示/隱藏清除按鈕
        if query:
            if not self.clear_btn.winfo_ismapped():
                self.clear_btn.pack(side="right", padx=(0, theme.styles.padding_small))
        else:
            if self.clear_btn.winfo_ismapped():
                self.clear_btn.pack_forget()
        
        # 觸發搜尋回調
        if self.on_search:
            self.on_search(query)
    
    def clear(self):
        """清除搜尋內容"""
        self.search_var.set("")
        self.search_entry.focus()
    
    def focus(self):
        """聚焦到搜尋框"""
        self.search_entry.focus()
        self.search_entry.select_range(0, 'end')
    
    def get_query(self) -> str:
        """
        獲取當前搜尋查詢
        
        Returns:
            str: 搜尋查詢
        """
        return self.search_var.get()
    
    def set_query(self, query: str):
        """
        設定搜尋查詢
        
        Args:
            query: 搜尋查詢
        """
        self.search_var.set(query)
    
    def update_placeholder(self, placeholder: str):
        """
        更新佔位符文字
        
        Args:
            placeholder: 新的佔位符文字
        """
        self.search_entry.configure(placeholder_text=placeholder)
    
    def _on_language_changed(self, old_language: str):
        """語言變更時的處理"""
        # 更新搜尋圖標文字
        self.search_icon.configure(text=t("common.search_colon"))
        # 更新佔位符文字
        self.update_placeholder(t("search.placeholder"))
    
    def destroy(self):
        """銷毀組件"""
        # 移除語言觀察者
        if hasattr(self, '_language_observer'):
            remove_language_observer(self._language_observer)
        
        super().destroy()