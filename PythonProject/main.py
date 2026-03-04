# main.py
from login import LoginWindow
from main_interface import MainInterface


def main():
    def on_login_success(user_manager):

        app = MainInterface(user_manager)
        app.run()

    login_app = LoginWindow(on_login_success)
    login_app.run()


if __name__ == '__main__':
    main()