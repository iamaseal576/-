# main_interface.py
import tkinter as tk
from tkinter import ttk, messagebox, font
from Users import (UserManager)
from kaimendaji import DoorGameGUI


class MainInterface:
    def __init__(self, user_manager):
        self.user_manager = user_manager
        self.current_user = user_manager.get_current_user()

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("开门大吉 - 主界面")
        self.root.geometry("600x500")

        # 设置字体
        self.title_font = font.Font(family="微软雅黑", size=24, weight="bold")
        self.normal_font = font.Font(family="微软雅黑", size=12)
        self.info_font = font.Font(family="微软雅黑", size=14, weight="bold")

        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="🎵 开门大吉 🎵",
                                font=self.title_font, foreground="#2E86C1")
        title_label.pack(pady=(0, 20))

        # 欢迎信息
        welcome_text = f"欢迎回来，{self.current_user['nickname']}！"
        welcome_label = ttk.Label(main_frame, text=welcome_text,
                                  font=self.info_font, foreground="#27AE60")
        welcome_label.pack(pady=10)

        # 用户信息卡片
        info_frame = ttk.Frame(main_frame, relief="solid", borderwidth=2)
        info_frame.pack(pady=20, fill=tk.X)

        ttk.Label(info_frame, text="当前用户信息",
                  font=self.normal_font, foreground="#2E86C1").pack(pady=5)

        ttk.Label(info_frame, text=f"账号: {self.current_user['account']}",
                  font=self.normal_font).pack(pady=2)
        ttk.Label(info_frame, text=f"昵称: {self.current_user['nickname']}",
                  font=self.normal_font).pack(pady=2)
        ttk.Label(info_frame, text=f"历史最高分: {self.current_user['high_score']} 分",
                  font=self.normal_font, foreground="#E74C3C").pack(pady=2)

        # 功能按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)

        # 个人信息按钮
        profile_btn = ttk.Button(btn_frame, text="👤 个人信息",
                                 command=self.show_profile, width=20)
        profile_btn.grid(row=0, column=0, padx=10, pady=10)

        # 开始挑战按钮
        game_btn = ttk.Button(btn_frame, text="🎮 开始挑战",
                              command=self.start_game, width=20)
        game_btn.grid(row=0, column=1, padx=10, pady=10)

        # 排行榜按钮
        rank_btn = ttk.Button(btn_frame, text="🏆 排行榜",
                              command=self.show_rankings, width=20)
        rank_btn.grid(row=1, column=0, padx=10, pady=10)

        # 退出登录按钮
        logout_btn = ttk.Button(btn_frame, text="🚪 退出登录",
                                command=self.logout, width=20)
        logout_btn.grid(row=1, column=1, padx=10, pady=10)

    def show_profile(self):
        """显示个人信息编辑窗口"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title("个人信息")
        profile_window.geometry("400x400")
        profile_window.transient(self.root)
        profile_window.grab_set()

        frame = ttk.Frame(profile_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 账号（不可修改）
        ttk.Label(frame, text="账号:", font=self.normal_font).grid(row=0, column=0, sticky=tk.W, pady=10)
        account_label = ttk.Label(frame, text=self.current_user['account'], font=self.normal_font)
        account_label.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)

        # 昵称
        ttk.Label(frame, text="新昵称:", font=self.normal_font).grid(row=1, column=0, sticky=tk.W, pady=10)
        nickname_entry = ttk.Entry(frame, width=25, font=self.normal_font)
        nickname_entry.insert(0, self.current_user['nickname'])
        nickname_entry.grid(row=1, column=1, pady=10, padx=10)

        # 新密码
        ttk.Label(frame, text="新密码:", font=self.normal_font).grid(row=2, column=0, sticky=tk.W, pady=10)
        password_entry = ttk.Entry(frame, width=25, font=self.normal_font, show="*")
        password_entry.grid(row=2, column=1, pady=10, padx=10)

        # 确认密码
        ttk.Label(frame, text="确认密码:", font=self.normal_font).grid(row=3, column=0, sticky=tk.W, pady=10)
        confirm_entry = ttk.Entry(frame, width=25, font=self.normal_font, show="*")
        confirm_entry.grid(row=3, column=1, pady=10, padx=10)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        # 保存按钮
        def save_profile():
            new_nickname = nickname_entry.get().strip()
            new_password = password_entry.get().strip()
            confirm = confirm_entry.get().strip()

            if new_password and new_password != confirm:
                messagebox.showwarning("提示", "两次输入的密码不一致")
                return

            if new_password and len(new_password) < 6:
                messagebox.showwarning("提示", "密码长度至少6位")
                return

            if self.user_manager.update_user_info(
                    self.current_user['account'],
                    new_nickname if new_nickname else None,
                    new_password if new_password else None
            ):
                # 更新当前用户信息
                self.current_user = self.user_manager.get_current_user()
                messagebox.showinfo("成功", "个人信息已更新！")
                profile_window.destroy()
                # 刷新主界面
                self.refresh_main_interface()
            else:
                messagebox.showerror("错误", "更新失败")

        save_btn = ttk.Button(button_frame, text="保存修改", command=save_profile, width=12)
        save_btn.grid(row=0, column=0, padx=5)

        # 注销账号按钮
        delete_btn = ttk.Button(button_frame, text="⚠️ 注销账号",
                                command=lambda: self.delete_account(profile_window), width=12)
        delete_btn.grid(row=0, column=1, padx=5)

    def delete_account(self, profile_window):
        """注销账号 - 需要密码验证"""
        # 创建密码验证窗口
        verify_window = tk.Toplevel(profile_window)
        verify_window.title("身份验证")
        verify_window.geometry("300x180")
        verify_window.transient(profile_window)
        verify_window.grab_set()

        verify_window.update_idletasks()
        width = verify_window.winfo_width()
        height = verify_window.winfo_height()
        x = (verify_window.winfo_screenwidth() // 2) - (width // 2)
        y = (verify_window.winfo_screenheight() // 2) - (height // 2)
        verify_window.geometry(f'300x180+{x}+{y}')

        frame = ttk.Frame(verify_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="请输入密码确认注销账号：",
                  font=self.normal_font).pack(pady=(0, 10))

        # 密码输入框
        password_entry = ttk.Entry(frame, width=20, font=self.normal_font, show="*")
        password_entry.pack(pady=10)
        password_entry.focus_set()

        password_entry.bind('<Return>', lambda e: verify_and_delete())

        def verify_and_delete():
            """验证密码并执行注销"""
            input_password = password_entry.get().strip()

            if not input_password:
                messagebox.showwarning("提示", "请输入密码")
                return

            # 验证密码
            current_password = self.current_user['password']  # MD5加密
            input_password_md5 = self.user_manager.md5_password(input_password)

            if input_password_md5 != current_password:
                messagebox.showerror("错误", "密码错误，注销失败")
                verify_window.destroy()
                return

            # 密码正确，关闭验证窗口
            verify_window.destroy()

            # 显示警告并请求二次确认
            if messagebox.askyesno("确认注销",
                                   f"确定要注销账号「{self.current_user['nickname']}」吗？\n\n"
                                   "⚠️ 警告：此操作不可恢复！\n"
                                   "所有游戏数据将被永久删除。",
                                   icon='warning'):
                # 二次确认
                if messagebox.askyesno("最终确认",
                                       "这是最后一次确认！\n\n"
                                       "点击「是」将永久删除您的账号和所有数据。",
                                       icon='warning'):
                    # 执行注销账号
                    if self.user_manager.delete_user(self.current_user['account']):
                        messagebox.showinfo("账号已注销", "您的账号已成功注销。")
                        profile_window.destroy()
                        self.root.destroy()
                        # 返回登录界面
                        from login import LoginWindow
                        login_app = LoginWindow(self.on_login_success)
                        login_app.run()
                    else:
                        messagebox.showerror("错误", "注销失败，请稍后重试。")

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        # 确认按钮
        confirm_btn = ttk.Button(button_frame, text="确认注销",
                                 command=verify_and_delete, width=10)
        confirm_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消",
                                command=verify_window.destroy, width=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def refresh_main_interface(self):
        """刷新主界面"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()

    def start_game(self):
        """开始游戏"""
        self.root.withdraw()  # 隐藏主界面

        # 创建游戏窗口
        game_root = tk.Toplevel()

        def on_game_close():
            """游戏窗口关闭时的处理"""
            try:
                game_root.destroy()  # 销毁游戏窗口
            except:
                pass
            self.root.deiconify()  # 显示主界面
            self.refresh_main_interface()

        # 创建游戏实例
        game_app = DoorGameGUI(game_root, self.user_manager, self.on_game_exit)

        # 设置窗口关闭事件
        game_root.protocol("WM_DELETE_WINDOW", on_game_close)

        # 等待游戏窗口关闭
        self.root.wait_window(game_root)

    def on_game_exit(self, final_score):
        """游戏退出回调"""
        # 更新历史最高分
        if final_score > self.current_user['high_score']:
            self.user_manager.update_user_info(
                self.current_user['account'],
                new_score=final_score
            )
            self.current_user = self.user_manager.get_current_user()

        # 显示主界面
        self.root.deiconify()
        self.refresh_main_interface()

    def on_game_close(self, game_root):
        """游戏窗口关闭"""
        game_root.destroy()
        self.root.deiconify()
        self.refresh_main_interface()

    def show_rankings(self):
        """显示排行榜"""
        rankings = self.user_manager.get_rankings(100)

        rank_window = tk.Toplevel(self.root)
        rank_window.title("排行榜 - 历史最高分前100名")
        rank_window.geometry("600x500")
        rank_window.transient(self.root)

        # 主框架
        main_frame = ttk.Frame(rank_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="🏆 玩家排行榜 🏆",
                                font=self.title_font, foreground="#2E86C1")
        title_label.pack(pady=(0, 20))

        # 创建表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动条
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建树形表格
        columns = ('排名', '昵称', '历史最高分', '注册时间')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                            yscrollcommand=scrollbar.set, height=15)

        # 设置列
        tree.column('排名', width=80, anchor='center')
        tree.column('昵称', width=150, anchor='center')
        tree.column('历史最高分', width=120, anchor='center')
        tree.column('注册时间', width=200, anchor='center')

        # 设置标题
        tree.heading('排名', text='排名')
        tree.heading('昵称', text='昵称')
        tree.heading('历史最高分', text='历史最高分')
        tree.heading('注册时间', text='注册时间')

        # 填充数据
        for i, user in enumerate(rankings, 1):
            values = (i, user['nickname'], user['high_score'], user['register_time'])
            tree.insert('', tk.END, values=values)

            # 高亮当前用户
            if user['account'] == self.current_user['account']:
                tree.tag_configure('current', background='#D5F4E6')
                tree.item(tree.get_children()[-1], tags=('current',))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)

        # 关闭按钮
        close_btn = ttk.Button(main_frame, text="关闭",
                               command=rank_window.destroy, width=15)
        close_btn.pack(pady=10)

    def logout(self):
        """退出登录"""
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.user_manager.logout()
            self.root.destroy()
            # 重新显示登录窗口
            from login import LoginWindow
            login_app = LoginWindow(self.on_login_success)
            login_app.run()

    def on_login_success(self, user_manager):
        """登录成功回调"""
        self.__init__(user_manager)
        self.run()

    def run(self):
        """运行主界面"""
        self.root.mainloop()