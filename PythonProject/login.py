# login_window.py
import tkinter as tk
from tkinter import ttk, messagebox, font
from Users import UserManager


class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.user_manager = UserManager()

        # 创建登录窗口
        self.window = tk.Tk()
        self.window.title("开门大吉 - 用户登录")
        self.window.geometry("400x450")
        self.window.resizable(False, False)

        # 设置字体
        self.title_font = font.Font(family="微软雅黑", size=20, weight="bold")
        self.normal_font = font.Font(family="微软雅黑", size=11)

        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="🎵 开门大吉 🎵",
                                font=self.title_font, foreground="#2E86C1")
        title_label.pack(pady=(0, 20))

        # 创建笔记本选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # 登录选项卡
        login_frame = ttk.Frame(notebook, padding="20")
        notebook.add(login_frame, text="登录")
        self.setup_login_tab(login_frame)

        # 注册选项卡
        register_frame = ttk.Frame(notebook, padding="20")
        notebook.add(register_frame, text="注册")
        self.setup_register_tab(register_frame)

    def setup_login_tab(self, parent):
        """设置登录选项卡"""
        # 账号
        ttk.Label(parent, text="账号:", font=self.normal_font).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.login_account = ttk.Entry(parent, width=25, font=self.normal_font)
        self.login_account.grid(row=0, column=1, pady=10, padx=10)

        # 密码
        ttk.Label(parent, text="密码:", font=self.normal_font).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.login_password = ttk.Entry(parent, width=25, font=self.normal_font, show="*")
        self.login_password.grid(row=1, column=1, pady=10, padx=10)

        # 登录按钮
        login_btn = ttk.Button(parent, text="登录", command=self.do_login, width=20)
        login_btn.grid(row=2, column=0, columnspan=2, pady=20)

        # 绑定回车键
        self.login_password.bind('<Return>', lambda e: self.do_login())

    def setup_register_tab(self, parent):
        """设置注册选项卡"""
        # 昵称
        ttk.Label(parent, text="昵称:", font=self.normal_font).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.reg_nickname = ttk.Entry(parent, width=25, font=self.normal_font)
        self.reg_nickname.grid(row=0, column=1, pady=10, padx=10)

        # 密码
        ttk.Label(parent, text="密码:", font=self.normal_font).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.reg_password = ttk.Entry(parent, width=25, font=self.normal_font, show="*")
        self.reg_password.grid(row=1, column=1, pady=10, padx=10)

        # 确认密码
        ttk.Label(parent, text="确认密码:", font=self.normal_font).grid(row=2, column=0, sticky=tk.W, pady=10)
        self.reg_confirm = ttk.Entry(parent, width=25, font=self.normal_font, show="*")
        self.reg_confirm.grid(row=2, column=1, pady=10, padx=10)

        # 注册按钮
        register_btn = ttk.Button(parent, text="注册", command=self.do_register, width=20)
        register_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # 提示信息
        hint_text = "系统将自动生成唯一账号\n注册后请牢记您的账号"
        hint_label = ttk.Label(parent, text=hint_text, font=self.normal_font, foreground="#7F8C8D")
        hint_label.grid(row=4, column=0, columnspan=2, pady=10)

    def do_login(self):
        """执行登录"""
        account = self.login_account.get().strip()
        password = self.login_password.get().strip()

        if not account or not password:
            messagebox.showwarning("提示", "请输入账号和密码")
            return

        success, result = self.user_manager.login(account, password)

        if success:
            messagebox.showinfo("成功", f"欢迎回来，{result['nickname']}！")
            self.window.destroy()
            self.on_login_success(self.user_manager)
        else:
            messagebox.showerror("错误", result)

    def do_register(self):
        """执行注册"""
        nickname = self.reg_nickname.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()

        if not nickname or not password:
            messagebox.showwarning("提示", "请填写昵称和密码")
            return

        if password != confirm:
            messagebox.showwarning("提示", "两次输入的密码不一致")
            return

        if len(password) < 6:
            messagebox.showwarning("提示", "密码长度至少6位")
            return

        success, result = self.user_manager.register(nickname, password)

        if success:
            account = result['account']
            messagebox.showinfo("注册成功",
                                f"您的账号已创建！\n\n账号: {account}\n昵称: {nickname}\n\n请牢记您的账号！")
            # 清空注册表单
            self.reg_nickname.delete(0, tk.END)
            self.reg_password.delete(0, tk.END)
            self.reg_confirm.delete(0, tk.END)
            # 切换到登录选项卡
            self.window.focus_set()
        else:
            messagebox.showerror("错误", result)

    def run(self):
        """运行窗口"""
        self.window.mainloop()