# plot_delay.py

import matplotlib.pyplot as plt
from matplotlib import style
import os

# 设置matplotlib的风格为'ggplot'
style.use('ggplot')

class RealTimePlot:
    def __init__(self):
        plt.ion()  # 开启interactive mode
        self.fig, self.ax = plt.subplots()
        self.x, self.y = [], []
        self.line, = self.ax.plot(self.x, self.y, 'r-', linewidth=2)  # 初始化一条红色线
        self.ax.set_xlabel('Time (s)')  # 设置X轴名字
        self.ax.set_ylabel('Average delay (s)')  # 设置Y轴名字
        
    def update_plot(self, time, total_delay):
        self.x.append(time)
        self.y.append(total_delay)
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.flush_events()

    def show_plot(self):
        plt.ioff()  # 关闭interactive mode
        plt.show()


    def save_plot(self, file_path = None, file_name = None):
        self.fig.savefig(file_path+file_name+'.png', dpi=300)  # 保存图片到文件
        self.fig.savefig(file_path+file_name+'.svg', dpi=300)  # 保存图片到文件
