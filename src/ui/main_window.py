"""
主視窗
應用程式的主要介面
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List, Dict
import os
import sys

# 新增父目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import OTPManager, OTPEntry, StorageManager
from src.utils import QRHandler, ExportImportManager
from src.ui.themes import theme
from src.ui.components import OTPCard, SearchBar, EmptyState


class MainWindow(ctk.CTk):
    """主視窗類別"""
    
    def __init__(self):
        super().__init__()
        
        # 設定視窗
        self.title("Easy OTP")
        self.geometry("450x700")
        self.minsize(400, 600)
        
        # 設定主題
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=theme.colors.bg_primary)
        
        # 初始化管理器
        self.otp_manager = OTPManager()
        self.storage_manager = StorageManager()
        self.export_import_manager = ExportImportManager(self.storage_manager)
        self.qr_handler = QRHandler()
        
        # 載入資料
        loaded_manager = self.storage_manager.load()
        if loaded_manager:
            self.otp_manager = loaded_manager
        
        # OTP 卡片字典
        self.otp_cards: Dict[str, OTPCard] = {}
        
        # 搜尋查詢
        self.search_query = ""
        
        # 創建 UI
        self._create_widgets()
        
        # 顯示 OTP 條目
        self._refresh_otp_list()
        
        # 開始更新循環
        self._update_otp_codes()
        
        # 綁定關閉事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 設定拖放
        self._setup_drag_drop()
    
    def _create_widgets(self):
        """創建組件"""
        # 頂部工具列
        self._create_toolbar()
        
        # 搜尋框
        self.search_bar = SearchBar(
            self,
            placeholder="搜尋 OTP...",
            on_search=self._on_search
        )
        self.search_bar.pack(fill="x", padx=theme.styles.padding_medium, 
                            pady=(0, theme.styles.padding_small))
        
        # 主要內容區域
        self._create_content_area()
        
        # 底部狀態列
        self._create_status_bar()
    
    def _create_toolbar(self):
        """創建工具列"""
        toolbar = ctk.CTkFrame(self, fg_color=theme.colors.bg_secondary, height=60)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)
        
        # 工具列內容
        toolbar_content = ctk.CTkFrame(toolbar, fg_color="transparent")
        toolbar_content.pack(fill="both", expand=True, padx=theme.styles.padding_medium,
                            pady=theme.styles.padding_small)
        
        # 標題
        title_label = ctk.CTkLabel(
            toolbar_content,
            text="Easy OTP",
            font=(theme.fonts.family_primary, theme.fonts.size_large, theme.fonts.weight_bold)
        )
        title_label.pack(side="left")
        
        # 右側按鈕
        button_frame = ctk.CTkFrame(toolbar_content, fg_color="transparent")
        button_frame.pack(side="right")
        
        # 新增按鈕（下拉選單）
        self.add_btn = ctk.CTkButton(
            button_frame,
            text="+ 新增",
            width=80,
            command=self._show_add_menu,
            **theme.get_button_style("primary")
        )
        self.add_btn.pack(side="left", padx=(0, theme.styles.margin_small))
        
        # 更多選項按鈕
        self.more_btn = ctk.CTkButton(
            button_frame,
            text="...",
            width=40,
            command=self._show_more_menu,
            **theme.get_button_style("secondary")
        )
        self.more_btn.pack(side="left")
    
    def _create_content_area(self):
        """創建內容區域"""
        # 滾動框架
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.colors.bg_primary,
            scrollbar_button_color=theme.colors.bg_tertiary,
            scrollbar_button_hover_color=theme.colors.bg_hover
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=theme.styles.padding_medium)
        
        # OTP 列表容器
        self.otp_list_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.otp_list_frame.pack(fill="both", expand=True)
        
        # 空狀態
        self.empty_state = EmptyState(
            self.otp_list_frame,
            title="還沒有任何 OTP",
            description="點擊上方「新增」按鈕開始",
            icon="🔐",
            action_text="上傳 QR Code",
            on_action=self._upload_qr_code
        )
    
    def _create_status_bar(self):
        """創建狀態列"""
        self.status_bar = ctk.CTkFrame(self, fg_color=theme.colors.bg_secondary, height=30)
        self.status_bar.pack(fill="x")
        self.status_bar.pack_propagate(False)
        
        # 狀態文字
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=(theme.fonts.family_primary, theme.fonts.size_small),
            text_color=theme.colors.text_secondary
        )
        self.status_label.pack(side="left", padx=theme.styles.padding_small)
        
        # 計數標籤
        self.count_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=(theme.fonts.family_primary, theme.fonts.size_small),
            text_color=theme.colors.text_secondary
        )
        self.count_label.pack(side="right", padx=theme.styles.padding_small)
        
        self._update_count_label()
    
    def _show_add_menu(self):
        """顯示新增選單"""
        # 創建選單
        menu = tk.Menu(self, tearoff=0, bg=theme.colors.bg_secondary,
                      fg=theme.colors.text_primary, activebackground=theme.colors.bg_hover)
        
        menu.add_command(label="上傳 QR Code", command=self._upload_qr_code)
        menu.add_command(label="手動輸入", command=self._manual_input)
        menu.add_separator()
        menu.add_command(label="批量導入", command=self._batch_import)
        
        # 顯示選單
        menu.tk_popup(
            self.add_btn.winfo_rootx(),
            self.add_btn.winfo_rooty() + self.add_btn.winfo_height()
        )
    
    def _show_more_menu(self):
        """顯示更多選項選單"""
        # 創建選單
        menu = tk.Menu(self, tearoff=0, bg=theme.colors.bg_secondary,
                      fg=theme.colors.text_primary, activebackground=theme.colors.bg_hover)
        
        menu.add_command(label="導出全部", command=self._export_all)
        menu.add_command(label="備份", command=self._create_backup)
        menu.add_separator()
        menu.add_command(label="關於", command=self._show_about)
        
        # 顯示選單
        menu.tk_popup(
            self.more_btn.winfo_rootx(),
            self.more_btn.winfo_rooty() + self.more_btn.winfo_height()
        )
    
    def _upload_qr_code(self):
        """上傳 QR Code"""
        file_path = filedialog.askopenfilename(
            title="選擇 QR Code 圖片",
            filetypes=[
                ("圖片檔案", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("所有檔案", "*.*")
            ]
        )
        
        if file_path:
            # 讀取 QR Code
            imported = self.export_import_manager.import_from_qr_image(
                self.otp_manager, file_path
            )
            
            if imported:
                self._save_data()
                self._refresh_otp_list()
                self._show_status(f"成功導入 {len(imported)} 個 OTP")
            else:
                messagebox.showerror("錯誤", "無法從圖片中讀取 OTP 資訊")
    
    def _manual_input(self):
        """手動輸入 OTP"""
        # 創建對話框
        dialog = ctk.CTkToplevel(self)
        dialog.title("手動新增 OTP")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(fg_color=theme.colors.bg_primary)
        
        # 居中顯示
        dialog.transient(self)
        dialog.grab_set()
        
        # 內容框架
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=theme.styles.padding_large,
                    pady=theme.styles.padding_large)
        
        # 標籤輸入
        ctk.CTkLabel(content, text="標籤名稱:", **theme.get_label_style()).pack(anchor="w")
        label_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        label_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 密鑰輸入
        ctk.CTkLabel(content, text="密鑰:", **theme.get_label_style()).pack(anchor="w")
        secret_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        secret_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 發行者輸入（可選）
        ctk.CTkLabel(content, text="發行者 (可選):", **theme.get_label_style()).pack(anchor="w")
        issuer_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        issuer_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 按鈕框架
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(theme.styles.padding_large, 0))
        
        # 確定按鈕
        def on_confirm():
            label = label_entry.get().strip()
            secret = secret_entry.get().strip()
            issuer = issuer_entry.get().strip() or None
            
            if not label or not secret:
                messagebox.showwarning("輸入錯誤", "請填寫標籤和密鑰", parent=dialog)
                return
            
            # 創建 OTP 條目
            entry = OTPEntry(label=label, secret=secret, issuer=issuer)
            
            if self.otp_manager.add_entry(entry):
                self._save_data()
                self._refresh_otp_list()
                self._show_status(f"已新增 {label}")
                dialog.destroy()
            else:
                messagebox.showerror("錯誤", "新增失敗，請檢查密鑰是否有效", parent=dialog)
        
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="確定",
            command=on_confirm,
            **theme.get_button_style("primary")
        )
        confirm_btn.pack(side="right", padx=(theme.styles.margin_small, 0))
        
        # 取消按鈕
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=dialog.destroy,
            **theme.get_button_style("secondary")
        )
        cancel_btn.pack(side="right")
        
        # 聚焦到第一個輸入框
        label_entry.focus()
    
    def _batch_import(self):
        """批量導入"""
        # 選擇導入方式
        dialog = ctk.CTkToplevel(self)
        dialog.title("批量導入")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.configure(fg_color=theme.colors.bg_primary)
        
        # 居中顯示
        dialog.transient(self)
        dialog.grab_set()
        
        # 內容
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=theme.styles.padding_large,
                    pady=theme.styles.padding_large)
        
        ctk.CTkLabel(
            content,
            text="選擇導入方式:",
            **theme.get_label_style()
        ).pack(pady=(0, theme.styles.padding_medium))
        
        # JSON 檔案按鈕
        def import_json():
            dialog.destroy()
            file_path = filedialog.askopenfilename(
                title="選擇 JSON 檔案",
                filetypes=[("JSON 檔案", "*.json"), ("所有檔案", "*.*")]
            )
            if file_path:
                manager = self.storage_manager.import_json(file_path)
                if manager:
                    # 合併條目
                    count = 0
                    for entry in manager.get_all_entries():
                        if self.otp_manager.add_entry(entry):
                            count += 1
                    
                    if count > 0:
                        self._save_data()
                        self._refresh_otp_list()
                        self._show_status(f"成功導入 {count} 個 OTP")
                    else:
                        messagebox.showinfo("提示", "沒有新的 OTP 可導入")
                else:
                    messagebox.showerror("錯誤", "無法讀取 JSON 檔案")
        
        json_btn = ctk.CTkButton(
            content,
            text="從 JSON 檔案導入",
            command=import_json,
            **theme.get_button_style("secondary")
        )
        json_btn.pack(fill="x", pady=theme.styles.margin_small)
        
        # QR Code 目錄按鈕
        def import_qr_dir():
            dialog.destroy()
            dir_path = filedialog.askdirectory(title="選擇包含 QR Code 的目錄")
            if dir_path:
                results = self.export_import_manager.import_from_qr_directory(
                    self.otp_manager, dir_path
                )
                
                if results:
                    total = sum(len(labels) for labels in results.values())
                    self._save_data()
                    self._refresh_otp_list()
                    self._show_status(f"從 {len(results)} 個檔案成功導入 {total} 個 OTP")
                else:
                    messagebox.showinfo("提示", "未找到任何 QR Code")
        
        qr_btn = ctk.CTkButton(
            content,
            text="從 QR Code 目錄導入",
            command=import_qr_dir,
            **theme.get_button_style("secondary")
        )
        qr_btn.pack(fill="x", pady=theme.styles.margin_small)
    
    def _export_all(self):
        """導出所有 OTP"""
        if not self.otp_manager.entries:
            messagebox.showinfo("提示", "沒有可導出的 OTP")
            return
        
        # 選擇導出方式
        dialog = ctk.CTkToplevel(self)
        dialog.title("導出 OTP")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.configure(fg_color=theme.colors.bg_primary)
        
        # 居中顯示
        dialog.transient(self)
        dialog.grab_set()
        
        # 內容
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=theme.styles.padding_large,
                    pady=theme.styles.padding_large)
        
        ctk.CTkLabel(
            content,
            text="選擇導出格式:",
            **theme.get_label_style()
        ).pack(pady=(0, theme.styles.padding_medium))
        
        # JSON 按鈕
        def export_json():
            dialog.destroy()
            file_path = filedialog.asksaveasfilename(
                title="儲存 JSON 檔案",
                defaultextension=".json",
                filetypes=[("JSON 檔案", "*.json"), ("所有檔案", "*.*")]
            )
            if file_path:
                if self.storage_manager.export_json(self.otp_manager, file_path):
                    self._show_status("成功導出為 JSON")
                else:
                    messagebox.showerror("錯誤", "導出失敗")
        
        json_btn = ctk.CTkButton(
            content,
            text="導出為 JSON",
            command=export_json,
            **theme.get_button_style("secondary")
        )
        json_btn.pack(fill="x", pady=theme.styles.margin_small)
        
        # QR Code 按鈕
        def export_qr():
            dialog.destroy()
            dir_path = filedialog.askdirectory(title="選擇導出目錄")
            if dir_path:
                results = self.export_import_manager.export_to_qr_codes(
                    self.otp_manager, dir_path
                )
                success_count = sum(1 for success in results.values() if success)
                self._show_status(f"成功導出 {success_count} 個 QR Code")
        
        qr_btn = ctk.CTkButton(
            content,
            text="導出為 QR Code",
            command=export_qr,
            **theme.get_button_style("secondary")
        )
        qr_btn.pack(fill="x", pady=theme.styles.margin_small)
        
        # CSV 按鈕
        def export_csv():
            dialog.destroy()
            file_path = filedialog.asksaveasfilename(
                title="儲存 CSV 檔案",
                defaultextension=".csv",
                filetypes=[("CSV 檔案", "*.csv"), ("所有檔案", "*.*")]
            )
            if file_path:
                if self.storage_manager.export_csv(self.otp_manager, file_path):
                    self._show_status("成功導出為 CSV")
                else:
                    messagebox.showerror("錯誤", "導出失敗")
        
        csv_btn = ctk.CTkButton(
            content,
            text="導出為 CSV",
            command=export_csv,
            **theme.get_button_style("secondary")
        )
        csv_btn.pack(fill="x", pady=theme.styles.margin_small)
    
    def _create_backup(self):
        """創建備份"""
        if not self.otp_manager.entries:
            messagebox.showinfo("提示", "沒有可備份的 OTP")
            return
        
        # 詢問備份名稱
        dialog = ctk.CTkInputDialog(
            text="輸入備份名稱（可選）:",
            title="創建備份"
        )
        backup_name = dialog.get_input()
        
        if backup_name is not None:  # 使用者沒有取消
            backup_path = self.export_import_manager.create_backup(
                self.otp_manager, backup_name if backup_name else None
            )
            
            if backup_path:
                self._show_status("備份創建成功")
                # 詢問是否開啟備份目錄
                if messagebox.askyesno("備份成功", "備份創建成功！\n是否開啟備份目錄？"):
                    os.startfile(backup_path)
            else:
                messagebox.showerror("錯誤", "備份創建失敗")
    
    def _show_about(self):
        """顯示關於對話框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("關於 Easy OTP")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.configure(fg_color=theme.colors.bg_primary)
        
        # 居中顯示
        dialog.transient(self)
        dialog.grab_set()
        
        # 內容
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=theme.styles.padding_large,
                    pady=theme.styles.padding_large)
        
        # Logo
        logo_label = ctk.CTkLabel(
            content,
            text="OTP",
            font=(theme.fonts.family_primary, 48, theme.fonts.weight_bold),
            text_color=theme.colors.accent_primary
        )
        logo_label.pack(pady=theme.styles.padding_small)
        
        # 標題
        title_label = ctk.CTkLabel(
            content,
            text="Easy OTP",
            font=(theme.fonts.family_primary, theme.fonts.size_large, theme.fonts.weight_bold)
        )
        title_label.pack()
        
        # 版本
        version_label = ctk.CTkLabel(
            content,
            text="版本 2.0.0",
            font=(theme.fonts.family_primary, theme.fonts.size_normal),
            text_color=theme.colors.text_secondary
        )
        version_label.pack(pady=theme.styles.padding_small)
        
        # 描述
        desc_label = ctk.CTkLabel(
            content,
            text="現代化的 OTP 管理器",
            font=(theme.fonts.family_primary, theme.fonts.size_normal),
            text_color=theme.colors.text_secondary
        )
        desc_label.pack()
        
        # 關閉按鈕
        close_btn = ctk.CTkButton(
            content,
            text="關閉",
            command=dialog.destroy,
            **theme.get_button_style("primary")
        )
        close_btn.pack(pady=(theme.styles.padding_large, 0))
    
    def _on_search(self, query: str):
        """處理搜尋"""
        self.search_query = query
        self._refresh_otp_list()
    
    def _refresh_otp_list(self):
        """刷新 OTP 列表"""
        # 清除現有卡片
        for card in self.otp_cards.values():
            card.destroy()
        self.otp_cards.clear()
        
        # 獲取要顯示的條目
        if self.search_query:
            entries = self.otp_manager.search_entries(self.search_query)
        else:
            entries = self.otp_manager.get_all_entries()
        
        # 顯示空狀態或條目
        if not entries:
            if self.search_query:
                self.empty_state.update_content(
                    title="找不到符合的 OTP",
                    description=f"沒有找到包含「{self.search_query}」的條目",
                    icon="🔍"
                )
            self.empty_state.pack(fill="both", expand=True)
        else:
            self.empty_state.pack_forget()
            
            # 創建 OTP 卡片
            for entry in entries:
                card = OTPCard(
                    self.otp_list_frame,
                    label=entry.label,
                    issuer=entry.issuer,
                    on_copy=lambda e=entry: self._copy_otp(e.label),
                    on_edit=lambda e=entry: self._edit_otp(e.label),
                    on_delete=lambda e=entry: self._delete_otp(e.label)
                )
                card.pack(fill="x", pady=theme.styles.margin_small)
                card.set_hover_effect(True)
                
                self.otp_cards[entry.label] = card
        
        # 更新計數
        self._update_count_label()
    
    def _copy_otp(self, label: str):
        """複製 OTP"""
        otp = self.otp_manager.generate_otp(label)
        if otp:
            self.clipboard_clear()
            self.clipboard_append(otp)
            self._show_status(f"已複製 {otp}")
    
    def _edit_otp(self, label: str):
        """編輯 OTP"""
        entry = self.otp_manager.get_entry(label)
        if not entry:
            return
        
        # 創建編輯對話框
        dialog = ctk.CTkToplevel(self)
        dialog.title("編輯 OTP")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(fg_color=theme.colors.bg_primary)
        
        # 居中顯示
        dialog.transient(self)
        dialog.grab_set()
        
        # 內容框架
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=theme.styles.padding_large,
                    pady=theme.styles.padding_large)
        
        # 標籤輸入
        ctk.CTkLabel(content, text="標籤名稱:", **theme.get_label_style()).pack(anchor="w")
        label_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        label_entry.insert(0, entry.label)
        label_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 密鑰輸入
        ctk.CTkLabel(content, text="密鑰:", **theme.get_label_style()).pack(anchor="w")
        secret_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        secret_entry.insert(0, entry.secret)
        secret_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 發行者輸入
        ctk.CTkLabel(content, text="發行者 (可選):", **theme.get_label_style()).pack(anchor="w")
        issuer_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        if entry.issuer:
            issuer_entry.insert(0, entry.issuer)
        issuer_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 按鈕框架
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(theme.styles.padding_large, 0))
        
        # 確定按鈕
        def on_confirm():
            new_label = label_entry.get().strip()
            new_secret = secret_entry.get().strip()
            new_issuer = issuer_entry.get().strip() or None
            
            if not new_label or not new_secret:
                messagebox.showwarning("輸入錯誤", "請填寫標籤和密鑰", parent=dialog)
                return
            
            # 創建新條目
            new_entry = OTPEntry(
                label=new_label,
                secret=new_secret,
                issuer=new_issuer,
                algorithm=entry.algorithm,
                digits=entry.digits,
                period=entry.period,
                tags=entry.tags,
                created_at=entry.created_at
            )
            
            if self.otp_manager.update_entry(label, new_entry):
                self._save_data()
                self._refresh_otp_list()
                self._show_status(f"已更新 {new_label}")
                dialog.destroy()
            else:
                messagebox.showerror("錯誤", "更新失敗", parent=dialog)
        
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="確定",
            command=on_confirm,
            **theme.get_button_style("primary")
        )
        confirm_btn.pack(side="right", padx=(theme.styles.margin_small, 0))
        
        # 取消按鈕
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=dialog.destroy,
            **theme.get_button_style("secondary")
        )
        cancel_btn.pack(side="right")
    
    def _delete_otp(self, label: str):
        """刪除 OTP（在 OTPCard 中已確認）"""
        if self.otp_manager.remove_entry(label):
            self._save_data()
            self._refresh_otp_list()
            self._show_status(f"已刪除 {label}")
    
    def _update_otp_codes(self):
        """更新所有 OTP 代碼"""
        for label, card in self.otp_cards.items():
            result = self.otp_manager.get_otp_with_remaining_time(label)
            if result:
                otp, remaining = result
                progress = self.otp_manager.get_progress(label)
                card.update_display(otp_code=otp, progress=progress)
        
        # 每秒更新一次
        self.after(1000, self._update_otp_codes)
    
    def _show_status(self, message: str, duration: int = 3000):
        """顯示狀態訊息"""
        self.status_label.configure(text=message)
        self.after(duration, lambda: self.status_label.configure(text=""))
    
    def _update_count_label(self):
        """更新計數標籤"""
        total = len(self.otp_manager.entries)
        if self.search_query:
            shown = len(self.otp_cards)
            self.count_label.configure(text=f"顯示 {shown} / {total} 個")
        else:
            self.count_label.configure(text=f"共 {total} 個")
    
    def _save_data(self):
        """儲存資料"""
        self.storage_manager.save(self.otp_manager)
    
    def _on_closing(self):
        """關閉視窗時的處理"""
        self._save_data()
        self.destroy()
    
    def _setup_drag_drop(self):
        """設定拖放功能"""
        try:
            from tkinterdnd2 import DND_FILES
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)
        except ImportError:
            # 如果沒有安裝 tkinterdnd2，跳過拖放功能
            pass
    
    def _on_drop(self, event):
        """處理拖放事件"""
        files = self.tk.splitlist(event.data)
        
        for file_path in files:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # 圖片檔案 - 嘗試讀取 QR Code
                imported = self.export_import_manager.import_from_qr_image(
                    self.otp_manager, file_path
                )
                if imported:
                    self._save_data()
                    self._refresh_otp_list()
                    self._show_status(f"從 {os.path.basename(file_path)} 導入 {len(imported)} 個 OTP")
            elif file_path.lower().endswith('.json'):
                # JSON 檔案
                manager = self.storage_manager.import_json(file_path)
                if manager:
                    count = 0
                    for entry in manager.get_all_entries():
                        if self.otp_manager.add_entry(entry):
                            count += 1
                    
                    if count > 0:
                        self._save_data()
                        self._refresh_otp_list()
                        self._show_status(f"從 {os.path.basename(file_path)} 導入 {count} 個 OTP")