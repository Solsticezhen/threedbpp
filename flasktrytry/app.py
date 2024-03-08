from flask import Flask, request, redirect, url_for, render_template, jsonify
import os
from src.trytry import optimize
import time
import threading
import shutil


app = Flask(__name__)
# 全局变量保存任务状态
task_completed = False
tables_list, images_list = [], []


# 定义一个MyThread.py线程类
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        time.sleep(2)
        self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None

    def alive(self):
        if self.is_alive() == 1:
            return 1
        else:
            return 0


def long_running_task(case_name, from_net):
    global tables_list, images_list
    global task_completed
    tables_list, images_list = [], []
    task_completed = False
    # 耗时任务
    tables_list, images_list = optimize(case_name, from_net)
    # result = optimize(case_name, from_net)
    # tables_list.append(result[0])
    # images_list.append(result[1])
    # 设置任务结果
    task_completed = True
    return tables_list, images_list


@app.route('/')
def start():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    # 检查是否有文件上传
    if 'file1' not in request.files or 'file2' not in request.files:
        return 'No files uploaded'

    # 获取上传的文件对象
    file1 = request.files['file1']
    file2 = request.files['file2']

    # print(file1.casename, file2.casename)
    # 检查文件名是否为空
    if file1.name == '' or file2.name == '':
        return 'No selected file'

    # 获取输入框的值
    case_name = request.form['case_name']

    # 如果目录存在，则删除目录
    if os.path.exists(f'./temp/data/{case_name}/'):
        shutil.rmtree(f'./temp/data/{case_name}/')

    # 再重新建一个
    os.makedirs(f'./temp/data/{case_name}/')

    # 保存上传的文件到服务器端的特定目录
    file1.save(f'./temp/data/{case_name}/containers_info.xlsx')
    file2.save(f'./temp/data/{case_name}/boxes_info.xlsx')

    # 返回成功消息
    return redirect(url_for('calculate', case_name=case_name))
    # return 'Files uploaded successfully'


@app.route('/calculate/<case_name>')
def calculate(case_name):
    # 检查是否有case_name上传
    if case_name is '':
        return render_template('upload.html')

    # 启动后台线程处理
    from_net = 1
    # 接收处理结果
    thread = MyThread(long_running_task, args=(case_name, from_net))
    thread.start()

    # while thread.alive():
    #     print(thread.alive())
    #     return "正在运算"

    # 重定向至处理页面
    return redirect(url_for('processing'))

    # thread.join()
    # tables, images = thread.get_result()
    #
    # # tables, images = optimize(case_name, from_net=1)
    # # tables, images = long_running_task(case_name, from_net=1)
    # # 等待任务处理完成
    #
    # return redirect(url_for('show_data', tables=tables, images=images))
    # # return 'yes!'


# 路由函数：检查任务状态
@app.route('/check_task_status')
def check_task_status():
    global task_completed
    return jsonify({'task_completed': task_completed})


# 正在处理的页面
@app.route('/processing')
def processing():
    return render_template('processing.html')


# 路由函数，渲染包含图像和表格的页面
@app.route('/show_data')
def show_data():
    global tables_list, images_list, task_completed
    if task_completed is True:
        return render_template('show_data.html', tables=tables_list, images=images_list)

    #
    # # tables, images = optimize(case_name, from_net=1)
    # # tables, images = long_running_task(case_name, from_net=1)
    # # 等待任务处理完成
    #
    # return redirect(url_for('show_data', tables=tables, images=images))
    # # return 'yes!'
    # 渲染模板并传递表格和图像数据
    # tables = request.args.getlist('tables')
    # images = request.args.getlist('images')
    # print(tables)
    # print(images)
    # return render_template('show_data.html', tables=tables_list, images=images_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
