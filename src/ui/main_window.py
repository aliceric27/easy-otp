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
from src.core.settings import settings
from src.utils import QRHandler, ExportImportManager
from src.utils.i18n import i18n, t, add_language_observer, remove_language_observer
from src.ui.themes import theme
from src.ui.components import OTPCard, SearchBar, EmptyState


class MainWindow(ctk.CTk):
    """主視窗類別"""
    
    def __init__(self):
        super().__init__()
        
        # 載入設定
        self._load_settings()
        
        # 設定視窗
        self.title(t("app.title"))
        window_settings = settings.get_window_settings()
        self.geometry(f"{window_settings['width']}x{window_settings['height']}")
        if window_settings['x'] and window_settings['y']:
            self.geometry(f"+{window_settings['x']}+{window_settings['y']}")
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
        
        # 註冊語言變更觀察者
        add_language_observer(self._on_language_changed)
    
    def _create_widgets(self):
        """創建組件"""
        # 頂部工具列
        self._create_toolbar()
        
        # 搜尋框
        self.search_bar = SearchBar(
            self,
            placeholder=t("search.placeholder"),
            on_search=self._on_search
        )
        self.search_bar.pack(fill="x", padx=theme.styles.padding_medium, 
                            pady=(theme.styles.padding_medium, theme.styles.padding_small))
        
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
        self.title_label = ctk.CTkLabel(
            toolbar_content,
            text=t("app.title"),
            font=(theme.fonts.family_primary, theme.fonts.size_large, theme.fonts.weight_bold)
        )
        self.title_label.pack(side="left")
        
        # 右側按鈕
        button_frame = ctk.CTkFrame(toolbar_content, fg_color="transparent")
        button_frame.pack(side="right")
        
        # 語言切換按鈕
        self.lang_btn = ctk.CTkButton(
            button_frame,
            text=self._get_language_display_text(),
            width=60,
            command=self._show_language_menu,
            **theme.get_button_style("secondary")
        )
        self.lang_btn.pack(side="left", padx=(0, theme.styles.margin_small))
        
        # 新增按鈕（下拉選單）
        self.add_btn = ctk.CTkButton(
            button_frame,
            text=t("menu.add.title"),
            width=80,
            command=self._show_add_menu,
            **theme.get_button_style("primary")
        )
        self.add_btn.pack(side="left", padx=(0, theme.styles.margin_small))
        
        # 更多選項按鈕
        self.more_btn = ctk.CTkButton(
            button_frame,
            text=t("menu.more.title"),
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
            title=t("empty_state.no_otp.title"),
            description=t("empty_state.no_otp.description"),
            icon="🔐",
            action_text=t("empty_state.no_otp.action"),
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
    
    def _load_settings(self):
        """載入設定"""
        # 設定語言
        saved_language = settings.get_language()
        i18n.set_language(saved_language)
    
    def _save_settings(self):
        """儲存設定"""
        # 儲存視窗大小和位置
        try:
            width = self.winfo_width()
            height = self.winfo_height()
            x = self.winfo_x()
            y = self.winfo_y()
            settings.set_window_settings(width, height, x, y)
        except:
            pass  # 如果無法取得視窗資訊，忽略
        
        # 儲存語言
        settings.set_language(i18n.get_current_language())
    
    def _get_language_display_text(self) -> str:
        """取得語言顯示文字"""
        current_lang = i18n.get_current_language()
        # 嘗試從翻譯檔案取得顯示文字
        display_key = f"menu.language.display.{current_lang}"
        display_text = t(display_key)
        # 如果找不到對應的顯示文字，使用預設邏輯
        if display_text == display_key:
            return current_lang[:2].upper()
        return display_text
    
    def _on_language_changed(self, old_language: str):
        """語言變更時的回調"""
        # 更新所有 UI 文字
        self._update_ui_texts()
        
        # 顯示狀態訊息
        current_lang_name = i18n.get_language_name(i18n.get_current_language())
        self._show_status(t("status.language_changed", language=current_lang_name))
    
    def _update_ui_texts(self):
        """更新所有 UI 文字"""
        # 更新標題
        self.title(t("app.title"))
        self.title_label.configure(text=t("app.title"))
        
        # 更新按鈕
        self.lang_btn.configure(text=self._get_language_display_text())
        self.add_btn.configure(text=t("menu.add.title"))
        self.more_btn.configure(text=t("menu.more.title"))
        
        # 更新搜尋框
        self.search_bar.update_placeholder(t("search.placeholder"))
        
        # 更新空狀態
        self.empty_state.update_content(
            title=t("empty_state.no_otp.title"),
            description=t("empty_state.no_otp.description"),
            action_text=t("empty_state.no_otp.action")
        )
        
        # 更新計數標籤
        self._update_count_label()
        
        # 重新刷新列表（以更新搜尋結果文字）
        if self.search_query:
            self._refresh_otp_list()
    
    def _show_language_menu(self):
        """顯示語言選單"""
        # 創建選單
        menu = tk.Menu(self, tearoff=0, bg=theme.colors.bg_secondary,
                      fg=theme.colors.text_primary, activebackground=theme.colors.bg_hover)
        
        # 取得可用語言
        available_languages = i18n.get_available_languages()
        current_language = i18n.get_current_language()
        
        for lang_code in available_languages:
            lang_name = i18n.get_language_name(lang_code)
            # 為當前語言加上標記
            display_name = f"✓ {lang_name}" if lang_code == current_language else lang_name
            menu.add_command(
                label=display_name,
                command=lambda code=lang_code: self._change_language(code)
            )
        
        # 顯示選單
        menu.tk_popup(
            self.lang_btn.winfo_rootx(),
            self.lang_btn.winfo_rooty() + self.lang_btn.winfo_height()
        )
    
    def _change_language(self, language_code: str):
        """切換語言"""
        if i18n.set_language(language_code):
            # 儲存設定
            settings.set_language(language_code)
    
    def _show_add_menu(self):
        """顯示新增選單"""
        # 創建選單
        menu = tk.Menu(self, tearoff=0, bg=theme.colors.bg_secondary,
                      fg=theme.colors.text_primary, activebackground=theme.colors.bg_hover)
        
        menu.add_command(label=t("menu.add.upload_qr"), command=self._upload_qr_code)
        menu.add_command(label=t("menu.add.manual_input"), command=self._manual_input)
        menu.add_separator()
        menu.add_command(label=t("menu.add.batch_import"), command=self._batch_import)
        
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
        
        menu.add_command(label=t("menu.more.export_all"), command=self._export_all)
        menu.add_command(label=t("menu.more.backup"), command=self._create_backup)
        menu.add_separator()
        menu.add_command(label=t("menu.more.about"), command=self._show_about)
        
        # 顯示選單
        menu.tk_popup(
            self.more_btn.winfo_rootx(),
            self.more_btn.winfo_rooty() + self.more_btn.winfo_height()
        )
    
    def _upload_qr_code(self):
        """上傳 QR Code"""
        file_path = filedialog.askopenfilename(
            title=t("file_dialog.select_qr"),
            filetypes=[
                (t("file_dialog.file_types.images"), "*.png *.jpg *.jpeg *.bmp *.gif"),
                (t("file_dialog.file_types.all"), "*.*")
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
                self._show_status(t("status.imported", count=len(imported)))
            else:
                messagebox.showerror(t("common.error"), t("error.qr_read_failed"), parent=self)
    
    def _manual_input(self):
        """手動輸入 OTP"""
        # 創建對話框
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("dialog.add_otp.title"))
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
        ctk.CTkLabel(content, text=t("dialog.add_otp.label"), **theme.get_label_style()).pack(anchor="w")
        label_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        label_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 密鑰輸入
        ctk.CTkLabel(content, text=t("dialog.add_otp.secret"), **theme.get_label_style()).pack(anchor="w")
        secret_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        secret_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 發行者輸入（可選）
        ctk.CTkLabel(content, text=t("dialog.add_otp.issuer"), **theme.get_label_style()).pack(anchor="w")
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
                messagebox.showwarning(t("common.warning"), t("dialog.add_otp.validation.required"), parent=dialog)
                return
            
            # 創建 OTP 條目
            entry = OTPEntry(label=label, secret=secret, issuer=issuer)
            
            if self.otp_manager.add_entry(entry):
                self._save_data()
                self._refresh_otp_list()
                self._show_status(t("status.added", label=label))
                dialog.destroy()
            else:
                messagebox.showerror(t("common.error"), t("dialog.add_otp.validation.invalid_secret"), parent=dialog)
        
        confirm_btn = ctk.CTkButton(
            button_frame,
            text=t("common.ok"),
            command=on_confirm,
            **theme.get_button_style("primary")
        )
        confirm_btn.pack(side="right", padx=(theme.styles.margin_small, 0))
        
        # 取消按鈕
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=t("common.cancel"),
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
        dialog.title(t("dialog.batch_import.title"))
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
            text=t("dialog.batch_import.choose_method"),
            **theme.get_label_style()
        ).pack(pady=(0, theme.styles.padding_medium))
        
        # JSON 檔案按鈕
        def import_json():
            dialog.destroy()
            file_path = filedialog.askopenfilename(
                title=t("file_dialog.select_json"),
                filetypes=[(t("file_dialog.file_types.json"), "*.json"), (t("file_dialog.file_types.all"), "*.*")]
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
                        self._show_status(t("status.imported", count=count))
                    else:
                        messagebox.showinfo(t("common.info"), t("dialog.batch_import.no_new_items"), parent=self)
                else:
                    messagebox.showerror(t("common.error"), t("error.json_read_failed"), parent=self)
        
        json_btn = ctk.CTkButton(
            content,
            text=t("dialog.batch_import.from_json"),
            command=import_json,
            **theme.get_button_style("secondary")
        )
        json_btn.pack(fill="x", pady=theme.styles.margin_small)
        
        # QR Code 目錄按鈕
        def import_qr_dir():
            dialog.destroy()
            dir_path = filedialog.askdirectory(title=t("file_dialog.select_qr_dir"))
            if dir_path:
                results = self.export_import_manager.import_from_qr_directory(
                    self.otp_manager, dir_path
                )
                
                if results:
                    total = sum(len(labels) for labels in results.values())
                    self._save_data()
                    self._refresh_otp_list()
                    self._show_status(t("status.import_from_dir", file_count=len(results), total=total))
                else:
                    messagebox.showinfo(t("common.info"), t("status.no_qr_found"), parent=self)
        
        qr_btn = ctk.CTkButton(
            content,
            text=t("dialog.batch_import.from_qr_dir"),
            command=import_qr_dir,
            **theme.get_button_style("secondary")
        )
        qr_btn.pack(fill="x", pady=theme.styles.margin_small)
    
    def _export_all(self):
        """導出所有 OTP"""
        if not self.otp_manager.entries:
            messagebox.showinfo(t("common.info"), t("dialog.export.no_items"), parent=self)
            return
        
        # 選擇導出方式
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("dialog.export.title"))
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
            text=t("dialog.export.choose_format"),
            **theme.get_label_style()
        ).pack(pady=(0, theme.styles.padding_medium))
        
        # JSON 按鈕
        def export_json():
            dialog.destroy()
            file_path = filedialog.asksaveasfilename(
                title=t("file_dialog.save_json"),
                defaultextension=".json",
                filetypes=[(t("file_dialog.file_types.json"), "*.json"), (t("file_dialog.file_types.all"), "*.*")]
            )
            if file_path:
                if self.storage_manager.export_json(self.otp_manager, file_path):
                    self._show_status(t("status.exported_json"))
                else:
                    messagebox.showerror(t("common.error"), t("error.export_failed"), parent=self)
        
        json_btn = ctk.CTkButton(
            content,
            text=t("dialog.export.json"),
            command=export_json,
            **theme.get_button_style("secondary")
        )
        json_btn.pack(fill="x", pady=theme.styles.margin_small)
        
        # QR Code 按鈕
        def export_qr():
            dialog.destroy()
            dir_path = filedialog.askdirectory(title=t("file_dialog.select_export_dir"))
            if dir_path:
                results = self.export_import_manager.export_to_qr_codes(
                    self.otp_manager, dir_path
                )
                success_count = sum(1 for success in results.values() if success)
                self._show_status(t("status.exported_qr", count=success_count))
        
        qr_btn = ctk.CTkButton(
            content,
            text=t("dialog.export.qr"),
            command=export_qr,
            **theme.get_button_style("secondary")
        )
        qr_btn.pack(fill="x", pady=theme.styles.margin_small)
        
        # CSV 按鈕
        def export_csv():
            dialog.destroy()
            file_path = filedialog.asksaveasfilename(
                title=t("file_dialog.save_csv"),
                defaultextension=".csv",
                filetypes=[(t("file_dialog.file_types.csv"), "*.csv"), (t("file_dialog.file_types.all"), "*.*")]
            )
            if file_path:
                if self.storage_manager.export_csv(self.otp_manager, file_path):
                    self._show_status(t("status.exported_csv"))
                else:
                    messagebox.showerror(t("common.error"), t("error.export_failed"), parent=self)
        
        csv_btn = ctk.CTkButton(
            content,
            text=t("dialog.export.csv"),
            command=export_csv,
            **theme.get_button_style("secondary")
        )
        csv_btn.pack(fill="x", pady=theme.styles.margin_small)
    
    def _create_backup(self):
        """創建備份"""
        if not self.otp_manager.entries:
            messagebox.showinfo(t("common.info"), t("dialog.backup.no_items"), parent=self)
            return
        
        # 詢問備份名稱
        dialog = ctk.CTkInputDialog(
            text=t("dialog.backup.name_prompt"),
            title=t("dialog.backup.title")
        )
        backup_name = dialog.get_input()
        
        if backup_name is not None:  # 使用者沒有取消
            backup_path = self.export_import_manager.create_backup(
                self.otp_manager, backup_name if backup_name else None
            )
            
            if backup_path:
                self._show_status(t("status.backup_created"))
                # 詢問是否開啟備份目錄
                if messagebox.askyesno(t("common.success"), t("dialog.backup.success"), parent=self):
                    os.startfile(backup_path)
            else:
                messagebox.showerror(t("common.error"), t("dialog.backup.failed"), parent=self)
    
    def _show_about(self):
        """顯示關於對話框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("dialog.about.title"))
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
            text=t("app.version"),
            font=(theme.fonts.family_primary, theme.fonts.size_normal),
            text_color=theme.colors.text_secondary
        )
        version_label.pack(pady=theme.styles.padding_small)
        
        # 描述
        desc_label = ctk.CTkLabel(
            content,
            text=t("app.description"),
            font=(theme.fonts.family_primary, theme.fonts.size_normal),
            text_color=theme.colors.text_secondary
        )
        desc_label.pack()
        
        # 關閉按鈕
        close_btn = ctk.CTkButton(
            content,
            text=t("common.close"),
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
                    title=t("search.no_results"),
                    description=t("search.no_results_desc", query=self.search_query),
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
            self._show_status(t("status.copied", code=otp))
    
    def _edit_otp(self, label: str):
        """編輯 OTP"""
        entry = self.otp_manager.get_entry(label)
        if not entry:
            return
        
        # 創建編輯對話框
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("dialog.edit_otp.title"))
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
        ctk.CTkLabel(content, text=t("dialog.edit_otp.label"), **theme.get_label_style()).pack(anchor="w")
        label_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        label_entry.insert(0, entry.label)
        label_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 密鑰輸入
        ctk.CTkLabel(content, text=t("dialog.edit_otp.secret"), **theme.get_label_style()).pack(anchor="w")
        secret_entry = ctk.CTkEntry(content, **theme.get_entry_style())
        secret_entry.insert(0, entry.secret)
        secret_entry.pack(fill="x", pady=(theme.styles.margin_small, theme.styles.margin_large))
        
        # 發行者輸入
        ctk.CTkLabel(content, text=t("dialog.edit_otp.issuer"), **theme.get_label_style()).pack(anchor="w")
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
                messagebox.showwarning(t("common.warning"), t("dialog.edit_otp.validation.required"), parent=dialog)
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
                self._show_status(t("status.updated", label=new_label))
                dialog.destroy()
            else:
                messagebox.showerror(t("common.error"), t("dialog.edit_otp.validation.invalid_secret"), parent=dialog)
        
        confirm_btn = ctk.CTkButton(
            button_frame,
            text=t("common.ok"),
            command=on_confirm,
            **theme.get_button_style("primary")
        )
        confirm_btn.pack(side="right", padx=(theme.styles.margin_small, 0))
        
        # 取消按鈕
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=t("common.cancel"),
            command=dialog.destroy,
            **theme.get_button_style("secondary")
        )
        cancel_btn.pack(side="right")
    
    def _delete_otp(self, label: str):
        """刪除 OTP（在 OTPCard 中已確認）"""
        if self.otp_manager.remove_entry(label):
            self._save_data()
            self._refresh_otp_list()
            self._show_status(t("status.deleted", label=label))
    
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
            self.count_label.configure(text=t("count.showing", shown=shown, total=total))
        else:
            self.count_label.configure(text=t("count.total", count=total))
    
    def _save_data(self):
        """儲存資料"""
        self.storage_manager.save(self.otp_manager)
    
    def _on_closing(self):
        """關閉視窗時的處理"""
        # 儲存設定
        self._save_settings()
        
        # 儲存 OTP 資料
        self._save_data()
        
        # 移除語言觀察者
        remove_language_observer(self._on_language_changed)
        
        self.destroy()
    
