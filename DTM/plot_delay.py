# plot_delay.py

import matplotlib.pyplot as plt
from matplotlib import style

# 设置matplotlib的风格为'ggplot'
style.use('ggplot')

class RealTimePlot:
    def __init__(self):
        plt.ion()  # 开启interactive mode
        self.fig, self.ax = plt.subplots()
        self.x, self.y = [], []
        self.line, = self.ax.plot(self.x, self.y, 'r-', linewidth=2)  # 初始化一条红色线

    def update_plot(self, time_step, total_delay):
        self.x.append(time_step)
        self.y.append(total_delay)
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.flush_events()

    def show_plot(self):
        plt.ioff()  # 关闭interactive mode
        plt.show()
