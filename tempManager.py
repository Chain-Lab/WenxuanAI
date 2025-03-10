"""
定时清理缓存文件夹
"""
import os
import threading
from fastapi import FastAPI
from contextlib import asynccontextmanager
from config import temp_path

class TempCleanScheduler:
    def __init__(self, interval=3600):
        self.interval = interval
        self.timer = None
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._schedule()

    def _schedule(self):
        if self.is_running:
            self.clean_temp()
            self.timer = threading.Timer(
                self.interval, 
                self._schedule
            )
            self.timer.start()

    def stop(self):
        if self.timer:
            self.timer.cancel()
        self.is_running = False

    @staticmethod
    def clean_temp():
        """具体的清理操作"""
        global temp_path
        print("[Server] 正在清理临时文件夹...")
        files = os.listdir(temp_path)
        for file in files:
            os.remove(os.path.join(temp_path, file))

@asynccontextmanager
async def async_temp_cleaner(app:FastAPI):
    scheduler = TempCleanScheduler(3600)
    scheduler.start()
    print("[Server] 定时清理任务已启动")
    yield
    scheduler.stop()
    print("[Server] 定时清理任务已停止")