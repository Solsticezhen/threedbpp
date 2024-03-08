import requests

# file_path = 'C:/Users/甄文至/Desktop/久章-装箱/data/测试1/containers_info.xlsx'
# with open(file_path, 'rb') as file:
#     excel_bytes = file.read()
#
# response = requests.post(url, files={'file': ('data.xlsx', excel_bytes)})
#
# print("Status Code:", response.status_code)
# print("1111Response Text:", response.text)


import requests
# 文件路径列表
file_paths = [
    'C:/Users/甄文至/Desktop/久章-装箱/data/测试1/containers_info.xlsx',
    'C:/Users/甄文至/Desktop/久章-装箱/data/测试1/boxes_info.xlsx',
    # 添加更多文件路径...
]

# 创建一个空的文件字典
files = {}

# 读取每个文件并添加到文件字典中
for file_path in file_paths:
    with open(file_path, 'rb') as file:
        files[file_path] = ('data.xlsx', file.read())

# 发送 POST 请求到服务器端
url = 'http://127.0.0.1:5000/upload'
response = requests.post(url, files=files)

# 输出服务器返回的响应
print(response.text)
