from distutils.core import setup, Extension
from Cython.Build import cythonize

setup(ext_modules = cythonize(Extension(
    'wuaiwow',       # 要生成的动态链接库的名字
    sources=['dot_cython.pyx'],  # 包含.pyx 文件,如果要调用C/C++,可以往里加.c/.cpp文件
    language='c',    # 默认是c,可改成c++
    include_dirs=[], # 传给 gcc 的 -I 参数
    library_dirs=[], # 传给 gcc 的 -L 参数
    libraries=[],    # 传给 gcc 的 -l 参数
    extra_compile_args=[], # 传给 gcc 的额外的编译参数，比方说你可以传一个 -std=c++11
    extra_link_args=[]     # 传给 gcc 的额外的链接参数（也就是生成动态链接库的时候用的）
)))

# python setup.py build_ext --inplace