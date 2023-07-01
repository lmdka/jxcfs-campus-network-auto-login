import json
import socket
import time
import requests
import ttkbootstrap as ttk
from configparser import ConfigParser
from threading import Thread

# 登录的默认信息
login_config = {
    'callback': 'dr1003',
    'login_method': '1',
    'user_account': '',
    'user_password': '',
    'wlan_user_ip': '',
    'wlan_user_ipv6': '',
    'wlan_user_mac': '000000000000',
    'wlan_ac_ip': '',
    'wlan_ac_name': '',
    'jsVersion': '4.1.3',
    'terminal_type': '1',
    'lang1': 'zh-cn',
    'v': '6571',
    'lang2': ' zh'
}


class App:
    def __init__(self):
        # 基础配置
        self.config = {
            'title': '江西外语外贸职业学院校园网自动登录器',
            'icon': 'logo.ico',
            'version': 'v1.0.1',
            'author': '小邝同学（雷姆的可爱）',
            'email': '2929957153@qq.com',
            'tips': '仅用于学习和测试'
        }
        # 创建app
        self.app = ttk.Window()
        # 设置标题
        self.app.title(self.config.get('title'))
        # 设置图标
        self.app.iconbitmap(self.config.get('icon'))
        # 设置置顶
        self.app.attributes('-topmost', True)
        # 设置不可拉伸窗口
        self.app.resizable(width=False, height=False)
        # 获取屏幕宽度
        self.window_width = self.app.winfo_screenwidth()
        # 获取屏幕高度
        self.window_height = self.app.winfo_screenheight()
        # 设置窗口宽度
        self.app_width = 520
        # 设置窗口高度
        self.app_height = 300
        # 设置窗口X轴位置
        self.window_x = (self.window_width - self.app_width) / 2
        # 设置窗口Y轴位置
        self.window_y = (self.window_height - self.app_height) / 2
        # 设置窗口显示位置
        self.app.geometry("%dx%d+%d+%d" % (self.app_width, self.app_height, self.window_x, self.window_y))

        # 动态账号对象
        self.user_account = ttk.StringVar()
        # 动态密码对象
        self.user_password = ttk.StringVar()
        # 是否保存账号密码
        self.is_save = ttk.IntVar()
        # 是否有开启自动登录
        self.auto_login = ttk.IntVar()
        # 日志
        self.logs = None

    def set_content(self):
        l1 = ttk.Label(master=self.app, text='账号')
        l1.grid(row=0, column=0, padx=10)
        l2 = ttk.Label(master=self.app, text='密码')
        l2.grid(row=1, column=0, padx=10)
        e1 = ttk.Entry(master=self.app, textvariable=self.user_account)
        e1.grid(row=0, column=1, padx=10)
        e2 = ttk.Entry(master=self.app, textvariable=self.user_password)
        e2.grid(row=1, column=1, padx=10)
        c1 = ttk.Checkbutton(master=self.app, text='记住密码', variable=self.is_save, onvalue=1, offvalue=0)
        c1.grid(row=0, column=3, padx=10)
        c2 = ttk.Checkbutton(master=self.app, text='自动登录', variable=self.auto_login, onvalue=1, offvalue=0)
        c2.grid(row=1, column=3, padx=10)
        b1 = ttk.Button(master=self.app, text='登录', width=10, command=self.click_login)
        b1.grid(row=0, rowspan=2, column=4, padx=10)
        self.logs = ttk.Text(master=self.app, width=50, height=10, exportselection=False, undo=False, wrap='char',
                             state=ttk.DISABLED)
        self.logs.grid(row=2, column=0, columnspan=5, pady=5, padx=5)

    def log(self, text):
        self.logs['state'] = ttk.NORMAL
        datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.logs.insert('1.0', f'[{datetime}] - {text}')
        self.logs['state'] = ttk.DISABLED

    def click_login(self):
        Thread(target=self.click_login_default).start()

    def click_login_default(self):
        global login_config
        config = load_config()
        save_config('config', 'auto_login', self.auto_login.get())
        save_config('config', 'is_save', self.is_save.get())
        save_config('params', 'user_account', self.user_account.get())
        if int(self.is_save.get()) == 1:
            save_config('params', 'user_account', self.user_account.get())
            save_config('params', 'user_password', self.user_password.get())
        self.log('保存配置完成\n')
        login_config['user_account'] = config.get('user_account')
        login_config['user_password'] = config.get('user_password')
        login_config['wlan_user_ip'] = refresh(socket.gethostbyname(socket.gethostname()))
        self.log('正在登录中...\n')
        response = login(config.get('login_url'), login_config)
        self.log(f'{response}\n')

    def on_auto_login(self):
        global login_config
        config = load_config()
        self.log(f'正在加载配置...\n')
        login_config['user_account'] = config.get('user_account')
        login_config['user_password'] = config.get('user_password')
        login_config['wlan_user_ip'] = refresh(socket.gethostbyname(socket.gethostname()))
        self.log(f'准备开始登录...\n')
        response = login(config.get('login_url'), login_config)
        self.log(f'正在登录中...\n')
        self.log(f'{response}\n')

    def info(self):
        for key in self.config:
            self.log(f'{self.config.get(key)}\n')

    def run(self):
        self.info()
        self.log(f'**********开启日志记录**********\n')
        if int(self.auto_login.get()) == 1:
            self.log(f'已设置自动登录\n')
            Thread(target=self.on_auto_login).start()
        else:
            self.log(f'未开启自动登录，请手动登录\n')
        self.app.mainloop()


def save_config(config_name, key, value):
    c = ConfigParser()
    c.read('setting.ini', encoding='utf-8')
    c.set(str(config_name), str(key), str(value))
    c.write(open('setting.ini', 'w'))
    return 'ok'


def login(url, params):
    response = requests.get(url=url, params=params)
    content = response.content.decode('utf-8')
    result = json.loads(content.split('(')[-1].split(')')[0])
    return result


def refresh(ip):
    if '172' not in ip:
        ip_list = []
        for index in socket.getaddrinfo(socket.gethostname(), None):
            ip = index[4][0]
            if not ip.startswith("127."):
                ip_list.append(ip)
        if len(ip_list) > 0:
            for use_ip in ip_list:
                if '172' in use_ip:
                    return use_ip
    else:
        return ip


# 加载配置文件
def load_config():
    c = ConfigParser()
    c.read('setting.ini', encoding='utf-8')
    auto_login = c.get('config', 'auto_login')
    is_save = c.get('config', 'is_save')
    login_url = c.get('config', 'login_url')
    user_account = c.get('params', 'user_account')
    user_password = c.get('params', 'user_password')
    setting = {
        'auto_login': auto_login,
        'is_save': is_save,
        'login_url': login_url,
        'user_account': user_account,
        'user_password': user_password
    }
    return setting


# 程序启动入口
def main():
    config = load_config()
    app = App()
    app.set_content()
    app.auto_login.set(int(config.get('auto_login')))
    app.is_save.set(int(config.get('is_save')))
    app.user_account.set(config.get('user_account'))
    app.user_password.set(config.get('user_password'))
    app.run()


if __name__ == '__main__':
    main()
