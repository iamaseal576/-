# user.py
import os
import time
import hashlib
from datetime import datetime


class UserManager:
    def __init__(self, user_file="user.txt"):
        # 始终使用当前工作目录（exe所在目录）
        self.user_file = os.path.join(os.getcwd(), user_file)
        self.current_user = None
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """确保用户文件存在"""
        if not os.path.exists(self.user_file):
            with open(self.user_file, 'w', encoding='utf-8') as f:
                f.write("# 账号|密码(MD5)|昵称|历史最高分|注册时间\n")

    def generate_account(self):
        """生成唯一账号（时间戳）"""
        return f"user_{int(time.time() * 1000)}"

    def md5_password(self, password):
        """MD5加密密码"""
        return hashlib.md5(password.encode()).hexdigest()

    def register(self, nickname, password):
        """用户注册"""
        # 检查昵称是否已存在
        users = self.get_all_users()
        for user in users:
            if user['nickname'] == nickname:
                return False, "昵称已存在"

        # 生成唯一账号
        account = self.generate_account()
        password_md5 = self.md5_password(password)
        register_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 写入文件
        with open(self.user_file, 'a', encoding='utf-8') as f:
            f.write(f"{account}|{password_md5}|{nickname}|0|{register_time}\n")

        return True, {"account": account, "nickname": nickname}

    def login(self, account, password):
        """用户登录"""
        password_md5 = self.md5_password(password)
        users = self.get_all_users()

        for user in users:
            if user['account'] == account and user['password'] == password_md5:
                self.current_user = user
                return True, user
        return False, "账号或密码错误"

    def delete_user(self, account):
        """删除用户账号"""
        users = self.get_all_users()
        new_users = [user for user in users if user['account'] != account]

        if len(new_users) < len(users):
            self.save_all_users(new_users)
            # 如果当前登录的用户被删除，清除current_user
            if self.current_user and self.current_user['account'] == account:
                self.current_user = None
            return True
        return False

    def get_all_users(self):
        """获取所有用户信息"""
        users = []
        try:
            with open(self.user_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split('|')
                    if len(parts) >= 5:
                        users.append({
                            'account': parts[0],
                            'password': parts[1],
                            'nickname': parts[2],
                            'high_score': int(parts[3]),
                            'register_time': parts[4]
                        })
        except Exception as e:
            print(f"读取用户文件失败: {e}")
        return users

    def update_user_info(self, account, new_nickname=None, new_password=None, new_score=None):
        """更新用户信息"""
        users = self.get_all_users()
        updated = False

        for user in users:
            if user['account'] == account:
                if new_nickname:
                    user['nickname'] = new_nickname
                if new_password:
                    user['password'] = self.md5_password(new_password)
                if new_score is not None and new_score > user['high_score']:
                    user['high_score'] = new_score
                updated = True
                if self.current_user and self.current_user['account'] == account:
                    self.current_user = user
                break

        if updated:
            self.save_all_users(users)
            return True
        return False

    def save_all_users(self, users):
        """保存所有用户信息到文件"""
        with open(self.user_file, 'w', encoding='utf-8') as f:
            f.write("# 账号|密码(MD5)|昵称|历史最高分|注册时间\n")
            for user in users:
                f.write(
                    f"{user['account']}|{user['password']}|{user['nickname']}|{user['high_score']}|{user['register_time']}\n")

    def get_rankings(self, limit=100):
        """获取排行榜（按历史最高分降序）"""
        users = self.get_all_users()
        # 按分数降序排序，取前limit名
        sorted_users = sorted(users, key=lambda x: x['high_score'], reverse=True)[:limit]
        return sorted_users

    def get_current_user(self):
        """获取当前登录用户"""
        return self.current_user

    def logout(self):
        """登出"""
        self.current_user = None