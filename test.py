import os
import sys

def get_resource_path(relative_path):
    """返回程序运行时的资源文件夹路径"""
    if getattr(sys, 'frozen', False):
        # 如果程序是通过 pyInstaller 打包的
        base_path = os.path.dirname(sys.executable)
    else:
        # 如果程序是以源代码的方式运行的
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, relative_path)

# 获取 Database 和 models 文件夹的路径
database_path = get_resource_path('Database')
models_path = get_resource_path('models')

print(f"Database Path: {database_path}")
print(f"Models Path: {models_path}")

# 你可以在这里继续使用 database_path 和 models_path 来加载相应的文件
