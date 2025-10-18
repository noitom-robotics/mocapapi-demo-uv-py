from setuptools import setup, find_packages
import os

packages = find_packages()

# 声明需要包含的非Python文件（lib目录下的所有文件）
package_data = {
    # 包名需与你的子工程包名一致（通常是目录名MocapApi）
    'mocap_api': [
        'lib/amd64/*.dll',    # Windows x64的DLL
        'lib/amd64/*.lib',    # 对应的lib文件（可选，若无需编译可省略）
        'lib/arm64/*.so',     # ARM64的SO库
        'lib/x86_64/*.so',    # x86_64的SO库
        'include/MocapApi/*.h',  # 头文件（若其他模块需要可保留）
    ]
}

setup(
    name="mocap_api",  # 包名（import 时使用的名称）
    version="0.0.67",             # 版本号
    packages=packages,  # 自动查找当前目录下的 Python 包
    package_data=package_data,  # 包含上述声明的非Python文件
    include_package_data=True,  # 强制打包所有声明的文件
    description='mocap_api with dynamic library support'
)