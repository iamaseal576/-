import tkinter as tk
from tkinter import ttk, messagebox, font
import subprocess
import os
import sys
import random
import threading
import time
from playsound import playsound

class DoorGameGUI:
    def __init__(self, root, user_manager=None, on_exit_callback=None):
        # 获取程序运行目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe，使用exe所在目录
            self.base_dir = os.path.dirname(sys.executable)
            # 资源文件在exe内部（_MEIPASS是PyInstaller临时解压目录）
            self.resource_dir = getattr(sys, '_MEIPASS', self.base_dir)
        else:
            # 如果是开发环境，使用当前文件所在目录
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            self.resource_dir = self.base_dir
        self.root = root
        self.user_manager = user_manager
        self.on_exit_callback = on_exit_callback
        self.root.title("开门大吉 - 音乐闯关游戏")
        self.root.geometry("800x600")

        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # 初始化
        self.score = 0
        self.current_door = 1
        self.max_doors = 12
        self.song_data = {}
        self.current_song_num = None
        self.is_playing = False

        # 设置字体
        self.title_font = font.Font(family="微软雅黑", size=24, weight="bold")
        self.door_font = font.Font(family="微软雅黑", size=48, weight="bold")
        self.score_font = font.Font(family="微软雅黑", size=18)
        self.normal_font = font.Font(family="微软雅黑", size=12)

        # 加载歌曲数据
        if not self.load_song_data():
            messagebox.showerror("错误", "无法加载歌曲数据文件，游戏无法继续！")
            self.root.destroy()
            return
        self.help_available = True
        self.help_used = False
        # 创建界面
        self.setup_ui()

    def load_song_data(self):
        """从txt文件加载歌曲数据"""
        try:
            data_file = os.path.join(self.resource_dir, "song_data.txt")
            # 如果资源目录没有，尝试在当前目录找
            if not os.path.exists(data_file):
                data_file = os.path.join(self.base_dir, "song_data.txt")
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue

                        parts = line.split('|')
                        if len(parts) >= 4:
                            try:
                                door_num = int(parts[0])
                                song_num = int(parts[1])
                                song_name = parts[2]
                                singer = parts[3]

                                door_key = str(door_num)
                                if door_key not in self.song_data:
                                    self.song_data[door_key] = {}

                                self.song_data[door_key][str(song_num)] = {
                                    'name': song_name,
                                    'singer': singer
                                }
                            except ValueError:
                                continue
                return True
            else:
                messagebox.showerror("错误", "找不到歌曲数据文件 song_data.txt")
                return False
        except Exception as e:
            messagebox.showerror("错误", f"加载歌曲数据失败: {e}")
            return False

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="🎵 开门大吉 🎵",
                                font=self.title_font, foreground="#2E86C1")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 门显示区域
        door_frame = ttk.Frame(main_frame, relief="solid", borderwidth=3)
        door_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=10, ipadx=5, ipady=5)

        self.door_label = tk.Label(door_frame, text=f"{self.current_door}",
                                   font=self.door_font,
                                   bg="#F4D03F",
                                   fg="#2C3E50",
                                   width=3,
                                   height=1)
        self.door_label.pack()

        door_text_label = ttk.Label(door_frame, text="号门", font=self.score_font)
        door_text_label.pack()

        # 分数显示
        score_frame = ttk.Frame(main_frame)
        score_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.score_label = ttk.Label(score_frame,
                                     text=f"🏆 当前分数: {self.score} 分",
                                     font=self.score_font,
                                     foreground="#E74C3C")
        self.score_label.pack()

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame,
                                            variable=self.progress_var,
                                            maximum=self.max_doors,
                                            length=400)
        self.progress_bar.grid(row=3, column=0, columnspan=3, pady=10)
        self.update_progress()

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        # 门铃按钮
        self.doorbell_btn = ttk.Button(button_frame,
                                       text="🎯 按响门铃",
                                       command=self.ring_doorbell,
                                       width=20)
        self.doorbell_btn.grid(row=0, column=0, padx=5, pady=5)

        # 播放状态
        self.play_status_label = ttk.Label(main_frame, text="", font=self.normal_font)
        self.play_status_label.grid(row=5, column=0, columnspan=3, pady=5)

        # 答案输入区域
        answer_frame = ttk.Frame(main_frame)
        answer_frame.grid(row=6, column=0, columnspan=3, pady=10)

        ttk.Label(answer_frame, text="请输入歌名：", font=self.normal_font).grid(row=0, column=0, padx=5)

        self.answer_entry = ttk.Entry(answer_frame, width=30, font=self.normal_font)
        self.answer_entry.grid(row=0, column=1, padx=5)
        self.answer_entry.bind('<Return>', lambda e: self.submit_answer())

        self.submit_btn = ttk.Button(answer_frame,
                                     text="提交答案",
                                     command=self.submit_answer,
                                     state='disabled')
        self.submit_btn.grid(row=0, column=2, padx=5)

        # 求助按钮
        self.help_btn = ttk.Button(answer_frame,
                                   text="❓ 求助（可用）",  # 初始显示可用
                                   command=self.get_help,
                                   state='disabled',  # 初始禁用，播放歌曲后启用
                                   width=15)
        self.help_btn.grid(row=0, column=3, padx=5)

        # 歌曲信息显示
        self.song_info_label = ttk.Label(main_frame, text="", font=self.normal_font)
        self.song_info_label.grid(row=7, column=0, columnspan=3, pady=5)

        # 操作按钮区域
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=8, column=0, columnspan=3, pady=20)

        self.continue_btn = ttk.Button(action_frame,
                                       text="🚪 继续挑战下一扇门",
                                       command=self.continue_game,
                                       state='disabled')
        self.continue_btn.grid(row=0, column=0, padx=10)

        self.quit_btn = ttk.Button(action_frame,
                                   text="💰 见好就收，带着奖金离开",
                                   command=self.quit_with_prize,
                                   state='disabled')
        self.quit_btn.grid(row=0, column=1, padx=10)

        # 游戏规则说明
        help_text = """游戏规则：
1. 共有12扇门，从1号门开始挑战
2. 点击"按响门铃"播放歌曲片段
3. 在输入框中输入歌名并提交，每一轮挑战限使用一次首字提醒求助机会
4. 猜对获得分数（分数=门序号），猜错分数清零
5. 每通过一扇门可选择继续或退出"""

        help_frame = ttk.Frame(main_frame)
        help_frame.grid(row=9, column=0, columnspan=3, pady=10, sticky=tk.W)

        help_label = ttk.Label(help_frame, text=help_text, font=self.normal_font,
                               justify=tk.LEFT, foreground="#7F8C8D")
        help_label.pack(anchor=tk.W)

        for i in range(3):
            main_frame.columnconfigure(i, weight=1)

    def update_progress(self):
        """更新进度条"""
        self.progress_var.set(self.current_door - 1)

    def ring_doorbell(self):
        """按响门铃"""
        if self.is_playing:
            return

        # 禁用门铃按钮
        self.doorbell_btn.config(state='disabled')
        self.play_status_label.config(text="🎵 正在播放歌曲...", foreground="#27AE60")

        # 在新线程中播放音乐
        threading.Thread(target=self.play_song_thread, daemon=True).start()

    def get_audio_path(self, door_num, song_num):
        """获取音频文件路径（处理打包后的情况）"""
        # 构建相对路径
        audio_relative = os.path.join("yinpin", str(door_num), f"{door_num}.{song_num}.mp3")

        # 先尝试从资源目录（打包内部）获取
        resource_path = os.path.join(self.resource_dir, audio_relative)
        if os.path.exists(resource_path):
            return resource_path

        # 再尝试从当前目录获取
        base_path = os.path.join(self.base_dir, audio_relative)
        if os.path.exists(base_path):
            return base_path

        # 如果都没有找到，返回None
        print(f"音频文件不存在: {audio_relative}")
        return None

    def play_song_thread(self):
        """在新线程中播放歌曲"""
        self.is_playing = True

        try:
            # 检查窗口是否还存在
            if not self.root.winfo_exists():
                print("窗口已关闭，停止播放")
                return

            # 获取当前门的歌曲数据
            door_key = str(self.current_door)
            if door_key not in self.song_data:
                if self.root.winfo_exists():
                    self.root.after(0, self.show_error, f"第{self.current_door}号门没有歌曲数据")
                return

            # 随机选择歌曲
            available_songs = list(self.song_data[door_key].keys())
            if not available_songs:
                if self.root.winfo_exists():
                    self.root.after(0, self.show_error, f"第{self.current_door}号门没有可用的歌曲")
                return

            self.current_song_num = random.choice(available_songs)

            # 获取音频路径
            audio_path = self.get_audio_path(self.current_door, self.current_song_num)

            if not audio_path:
                if self.root.winfo_exists():
                    self.root.after(0, self.show_error, f"音频文件不存在")
                return

            # 播放音频
            try:
                # 使用 playsound 播放（会阻塞直到播放完成）
                playsound(audio_path)

                # 播放完成后，检查窗口是否还存在
                if self.root.winfo_exists():
                    time.sleep(0.2)
                    self.root.after(0, self.on_song_finished)
                else:
                    print("窗口已关闭，不更新UI")

            except Exception as e:
                print(f"playsound播放错误: {e}")

                # 备用播放方法
                try:
                    if sys.platform == 'win32':
                        import winsound
                        winsound.PlaySound(audio_path, winsound.SND_FILENAME)
                    elif sys.platform == 'darwin':
                        subprocess.run(['afplay', audio_path])
                    else:
                        subprocess.run(['aplay', audio_path])

                    if self.root.winfo_exists():
                        time.sleep(0.2)
                        self.root.after(0, self.on_song_finished)

                except Exception as e2:
                    print(f"备选播放方法也失败: {e2}")
                    if self.root.winfo_exists():
                        self.root.after(0, self.show_error, "播放失败，请检查音频文件")

        except Exception as e:
            print(f"播放线程发生未预期错误: {e}")
            try:
                if self.root.winfo_exists():
                    self.root.after(0, self.show_error, f"播放出错: {str(e)}")
            except:
                pass

        finally:
            self.is_playing = False


    def play_audio(self, audio_path):
        """使用playsound播放音频文件"""
        if not os.path.exists(audio_path):
            print(f"文件不存在: {audio_path}")
            return False

        try:
            # 使用 playsound（异步播放）
            playsound(audio_path)
            return True

        except Exception as e:
            print(f"playsound播放错误: {e}")
            print(f"错误类型: {type(e).__name__}")

            # 如果playsound失败，尝试使用系统命令（备选方案）
            try:
                if sys.platform == 'win32':
                    # Windows系统
                    import winsound
                    winsound.PlaySound(audio_path, winsound.SND_FILENAME)
                    return True
                elif sys.platform == 'darwin':
                    # macOS系统
                    subprocess.run(['afplay', audio_path])
                    return True
                else:
                    # Linux系统
                    subprocess.run(['aplay', audio_path])
                    return True
            except Exception as e2:
                print(f"备选播放方法也失败: {e2}")
                return False

    def on_song_finished(self):
        """歌曲播放完成后的处理"""
        self.play_status_label.config(text="✅ 歌曲播放完毕，请输入歌名", foreground="#2E86C1")
        self.submit_btn.config(state='normal')

        # 只有在求助还可用时才启用求助按钮
        if self.help_available and not self.help_used:
            self.help_btn.config(state='normal')
            self.help_btn.config(text="❓ 求助（可用）")
        else:
            self.help_btn.config(state='disabled')
            self.help_btn.config(text="❓ 求助（已用）")

        self.answer_entry.focus_set()

        self.song_info_label.config(text="提示：请输入完整的歌曲名称")

    def show_error(self, message):
        """显示错误信息"""
        self.play_status_label.config(text=f"❌ {message}", foreground="#E74C3C")
        self.doorbell_btn.config(state='normal')

    def submit_answer(self):
        """提交答案"""
        user_answer = self.answer_entry.get().strip()
        if not user_answer:
            messagebox.showwarning("提示", "请输入歌名")
            return

        is_correct, song_info = self.check_answer(
            self.current_door,
            self.current_song_num,
            user_answer
        )

        if is_correct:
            # 回答正确
            self.score += self.current_door
            self.score_label.config(text=f"🏆 当前分数: {self.score} 分")

            # 显示正确信息
            self.show_result_message(
                "🎉 恭喜你！回答正确！",
                f"歌曲: {song_info['name']} 原唱: {song_info['singer']} 获得 {self.current_door} 分！",
                "success"
            )

            # 如果是第12扇门，显示通关消息，不启用继续按钮
            if self.current_door == self.max_doors:
                self.show_victory_message()
                if self.continue_btn.winfo_exists():
                    self.continue_btn.config(state='disabled')
            else:
                # 启用继续和退出按钮
                if self.continue_btn.winfo_exists():
                    self.continue_btn.config(state='normal')
                if self.quit_btn.winfo_exists():
                    self.quit_btn.config(state='normal')
            # 禁用提交按钮和输入框
            if self.submit_btn.winfo_exists():
                self.submit_btn.config(state='disabled')
            if self.answer_entry.winfo_exists():
                self.answer_entry.config(state='disabled')
            if self.help_btn.winfo_exists():
                self.help_btn.config(state='disabled')
        else:
            # 回答错误
            self.score = 0
            self.score_label.config(text=f"🏆 当前分数: {self.score} 分")

            # 显示错误信息
            self.show_result_message(
                "❌ 很遗憾，回答错误！",
                f"正确答案: {song_info['name']} 原唱: {song_info['singer']} 所有分数清零！",
                "error"
            )

            # 询问是否重新开始或返回主界面
            try:
                result = messagebox.askyesnocancel("游戏结束",
                                                   "是否重新开始游戏？\n\n选择'是'重新开始\n选择'否'返回主界面")
                if result is True:  # 是 - 重新开始
                    self.restart_game()
                elif result is False:  # 否 - 返回主界面
                    self.quit_game()
            except:
                # 如果窗口已关闭，忽略错误
                pass

    def check_answer(self, door_num, song_num, user_input):
        """检查用户答案是否正确"""
        door_key = str(door_num)
        if door_key in self.song_data and str(song_num) in self.song_data[door_key]:
            correct_song = self.song_data[door_key][str(song_num)]
            correct_name = correct_song['name']

            # 清理输入
            def clean_text(text):
                return text.replace('《', '').replace('》', '').replace(' ', '').lower()

            user_clean = clean_text(user_input)
            correct_clean = clean_text(correct_name)

            # 判断是否匹配
            if user_clean == correct_clean:
                return True, correct_song
            else:
                return False, correct_song
        return False, None

    def show_result_message(self, title, message, msg_type):
        """显示结果消息"""
        if msg_type == "success":
            bg_color = "#D5F4E6"
            fg_color = "#27AE60"
        else:
            bg_color = "#FADBD8"
            fg_color = "#E74C3C"

        self.song_info_label.config(
            text=message,
            background=bg_color,
            foreground=fg_color,
            relief="solid",
            borderwidth=2,
            padding=10
        )

    def continue_game(self):
        """继续下一扇门"""
        self.current_door += 1

        if self.current_door > self.max_doors:
            self.show_victory_message()
            return

        # 更新门显示
        self.door_label.config(text=f"{self.current_door}")

        # 更新进度条
        self.update_progress()

        # 重置界面状态
        self.reset_interface()

    def get_help(self):
        """获取求助（显示歌名首字）"""
        if not self.help_available or self.help_used:
            messagebox.showinfo("提示", "求助机会已用完！")
            return

        if not self.current_song_num:
            messagebox.showwarning("提示", "请先播放歌曲！")
            return

        # 获取当前歌曲信息
        door_key = str(self.current_door)
        if door_key in self.song_data and str(self.current_song_num) in self.song_data[door_key]:
            song_info = self.song_data[door_key][str(self.current_song_num)]
            song_name = song_info['name']

            # 获取歌名首字（处理可能的书名号）
            if song_name.startswith('《'):
                first_char = song_name[1]  # 跳过《
            else:
                first_char = song_name[0]

            # 显示提示对话框
            messagebox.showinfo("求助提示",
                                f"🎵 歌名首字提示：{first_char}\n\n（本轮求助机会已使用）")

            # 标记求助已使用
            self.help_used = True
            self.help_available = False

            # 更新按钮状态
            self.help_btn.config(state='disabled')
            self.help_btn.config(text="❓ 求助（已用）")

    def reset_interface(self):
        """重置界面状态"""
        # 清空输入框和显示，确保自动清空
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state='normal')
        self.song_info_label.config(text="加油！", background=self.root.cget('bg'),foreground="#7F8C8D")

        # 重置按钮状态
        self.doorbell_btn.config(state='normal')
        self.submit_btn.config(state='disabled')
        # 求助按钮状态根据求助是否可用设置
        if self.help_available and not self.help_used:
            self.help_btn.config(state='disabled')  # 等待歌曲播放后启用
            self.help_btn.config(text="❓ 求助（可用）")
        else:
            self.help_btn.config(state='disabled')
            self.help_btn.config(text="❓ 求助（已用）")
        self.continue_btn.config(state='disabled')
        self.quit_btn.config(state='disabled')

        # 更新状态标签
        self.play_status_label.config(text="点击'按响门铃'开始播放歌曲", foreground="#7F8C8D")

    def on_window_close(self):
        """窗口关闭事件"""
        self.quit_game()

    def quit_game(self):
        """退出游戏并返回主界面"""
        if self.on_exit_callback:
            self.on_exit_callback(self.score)
        self.root.destroy()


    def quit_with_prize(self):
        """带着奖金退出"""
        if messagebox.askyesno("见好就收",
                               f"你确定要带着 {self.score} 分离开吗？"):
            messagebox.showinfo("恭喜", f"🎉 恭喜你带着 {self.score} 分安全离开！")
            self.quit_game()

    def restart_game(self):
        """重新开始游戏"""
        if messagebox.askyesno("重新开始", "确定要重新开始游戏吗？"):
            self.score = 0
            self.current_door = 1

        # 更新显示
        self.score_label.config(text=f"🏆 当前分数: {self.score} 分")
        self.door_label.config(text=f"{self.current_door}")
        self.update_progress()

        # 重置求助状态
        self.help_used = False
        self.help_available = True

        # 重置界面
        self.reset_interface()

        self.song_info_label.config(text="加油！", foreground="#7F8C8D")

    def show_victory_message(self):
        """显示通关消息 - 修改为不自动退出"""
        messagebox.showinfo(
            "🎉 通关成功！",
            f"恭喜你成功通关所有12扇门！\n🏆 最终得分: {self.score} 分\n你是真正的音乐达人！"
        )
        self.continue_btn.config(state='disabled')
        self.play_status_label.config(text="🎉 已通关所有门！", foreground="#2E86C1")
        if messagebox.askyesno("通关", "是否返回主界面？"):
            self.quit_game()


def main():
    root = tk.Tk()

    try:
        root.iconbitmap('icon.ico')  # 如果有图标文件
    except:
        pass

    app = DoorGameGUI(root)
    root.mainloop()

