import psutil
import time
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item
import threading
def find_and_kill_processes(process_names, last_pids):
    found_pids = {}
    killed_process = False  # 添加一个标志来指示是否终止了进程
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in process_names:
                pid = proc.info['pid']
                process_name = proc.info['name']
                found_pids[process_name] = pid
                if process_name not in last_pids or pid != last_pids[process_name]:
                    p = psutil.Process(pid)
                    p.terminate()
                    p.wait()
                    print(f"进程 {process_name} (PID: {pid}) 已结束。")
                    killed_process = True  # 设置标志为True
                else:
                    print(f"进程 {process_name} (PID: {pid}) 未重启。")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"处理进程 {process_name} (PID: {pid}) 时出错: {e}")
    return found_pids, killed_process
def on_quit(icon, item):
    icon.stop()
    exit(0)
def create_image(color=(255, 255, 255)):
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color)
    return image
def update_icon(icon, killed_process):
    if killed_process:
        icon.icon = create_image((255, 0, 0))  # 红色
    else:
        icon.icon = create_image((255, 255, 255))  # 白色
    icon.visible = True
def run_in_thread(icon):
    global last_pids
    while True:
        last_pids, killed_process = find_and_kill_processes(target_process_names, last_pids)
        update_icon(icon, killed_process)
        time.sleep(interval)
def read_config():
    config = {}
    try:
        with open('config.txt', 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value
    except FileNotFoundError:
        print("配置文件不存在，使用默认设置。")
    return config
if __name__ == "__main__":
    config = read_config()
    target_process_names = config.get('processes', "msedge.exe,WeChat.exe").split(',')
    interval = float(config.get('interval', 0.1))
    last_pids = {}

    menu = (item('退出', on_quit),)
    icon = pystray.Icon("name", create_image(), "进程监控", menu)

    threading.Thread(target=run_in_thread, args=(icon,), daemon=True).start()
    icon.run()