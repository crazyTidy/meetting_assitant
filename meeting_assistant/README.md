# meeting_assistant


## 1.简介

FastApi 模块工程模板。


## 2.使用说明

本仓库 **meeting_assistant** 是 **FastApi 应用** 的 **子模块工程模板**。 该工程可以 **独立开发**，**独立运行**，并在必要时，可以由 **fastapi_application_template** 引用集成。


### 2.1.工程目录

```
.
├── meeting_assistant             # 子模块名
│   ├── dependencies                    # 依赖项模块
│   │   ├── __init__.py
│   ├── docs                            # 相关文档与手册
│   │   ├── manual.md                   # 手册文档
│   ├── items                           # 数据结构模块，基于 pydantic，主要用于对请求与响应的自动化解析
│   │   ├── __init__.py
│   │   ├── user_item.py                # 用户数据结构
│   ├── logs                            # 日志文件目录
│   │   ├── .gitkeep
│   ├── middlewares                     # 中间件目录
│   │   ├── __init__.py
│   │   ├── permission_middleware.py    # 权限中间件
│   │   ├── session_middleware.py       # 会话中间件
│   ├── models                          # 数据库 ORM 模块
│   │   ├── __init__.py
│   │   ├── base_model.py               # 基本表父类 BaseModel，用于继承
│   │   ├── database.py                 # 数据库连接构建与维护
│   │   ├── user_model.py               # 用户表，继承 BaseModel
│   ├── routers                         # 路由模块
│   │   ├── __init__.py
│   │   ├── swagger_router.py           # swagger 子路由，请勿删除
│   │   ├── hello_world_router.py       # hello_world 子路由，使用时，请删除
│   ├── scripts                         # 脚本目录，区分 linux 平台与 windows 平台
│   │   ├── complie.sh                  # 自动化编译脚本
│   │   ├── complie.bat                 # 
│   │   ├── environment.sh              # 程序启动环境变量脚本，可以 source environment.sh 直接加载
│   │   ├── environment.bat             # 同上，可以 call environment.bat 直接加载
│   │   ├── format.sh                   # 代码格式化脚本，依赖 isort 和 black
│   │   ├── format.bat                  # 
│   │   ├── restart.sh                  # 重启脚本
│   │   ├── restart.bat                 # 
│   │   ├── start.sh                    # 启动脚本
│   │   ├── start.bat                   # 
│   │   ├── stop.sh                     # 停止脚本
│   │   ├── stop.bat                    # 
│   ├── services                        # 服务逻辑模块
│   │   ├── __init__.py
│   ├── settings                        # 配置模块
│   │   ├── __init__.py
│   │   ├── directory_config.py         # 目录配置，可以直接引用
│   │   ├── environment_config.py       # 运行环境配置，主要用于存储启动配置项，请与 environment.sh 保持一致
│   │   ├── file_config.py              # 静态文件配置
│   ├── statics                         # 静态资源目录
│   │   ├── certificates                # 证书目录
│   │   │   ├── ca.crt                  # 根签名
│   │   │   ├── server.crt              # 服务端签名
│   │   │   ├── server.pem              # 服务端证书
│   │   ├── icons                       # 图标目录
│   │   │   ├── favicon.png             # favicon 图标
│   │   ├── javascripts                 # javascript 脚本目录
│   │   │   ├── swagger-ui-bundle.js    # swagger 脚本
│   │   ├── jsons                       # json 数据目录
│   │   │   ├── .gitkeep
│   │   ├── styles                      # 布局文件目录
│   │   │   ├── swagger-ui.css          # swagger 布局文件
│   ├── temps                           # 缓存目录
│   │   ├── .gitkeep
│   ├── tests                           # 测试代码目录
│   │   ├── configurations              # 启动配置样例目录
│   │   │   ├── config.json             # json 格式
│   │   │   ├── config.ini              # ini 格式
│   │   │   ├── config.yaml             # yaml 格式
│   │   ├── __init__.py
│   │   ├── test_file_util.py           # 测试 file_util 工具文件
│   │   ├── test_hello_world.py         # 测试 hello_world 接口文件
│   │   ├── test_http_util.py           # 测试 http_util 工具文件
│   │   ├── test_jwt_util.py            # 测试 jwt_util 工具文件
│   │   ├── test_minio_client.py        # 测试 minio_client 工具文件
│   │   ├── test_redis_client.py        # 测试 redis_client 工具文件
│   ├── tools                           # 命令行工具类目录
│   │   ├── __init__.py
│   │   ├── command_tool.py             # 命令行工具模板方法
│   │   ├── database_tool.py            # 数据库命令行工具
│   └── utils                           # 第三方、工具、常量、异常等公用工具模块
│   │   ├── clients                     # 客户端工具目录
│   │   │   ├── minio_client.py         # minio 客户端工具
│   │   │   ├── redis_client.py         # redis 客户端工具
│   │   ├── __init__.py
│   │   ├── file_util.py                # 文件工具
│   │   ├── hash_util.py                # 哈希工具
│   │   ├── http_util.py                # 网络请求工具
│   │   ├── jwt_util.py                 # JWT 认证工具
│   │   ├── log_util.py                 # 日志工具
│   │   ├── module_util.py              # 模块工具
│   │   ├── string_util.py              # 字符串工具
│   ├── __init__.py
│   ├── .gitignore
│   ├── app.py                          # 启动项目入口文件
│   ├── compile_app.py                  # 应用服务编译可执行文件入口文件
│   ├── compile_tool.py                 # 应用工具编译可执行文件入口文件
│   ├── cython_setup.py                 # cython 编译脚本文件
│   ├── LICENSE                         # 共享许可证
│   ├── pip_requirements.py             # 项目运行环境依赖包安装脚本
│   ├── pyinstaller_setup.py            # pyinstaller 编译脚本文件
│   ├── README.md                       # 项目说明文档
│   ├── requirements.py                 # 项目运行环境依赖包生成脚本
│   ├── requirements.txt                # 项目运行环境依赖包
```

下面主要以 **linux 平台** 为主介绍相关使用步骤，**windows 平台** 可以参考执行。


### 2.2.初始化步骤

初始化安装相关依赖包

```BASH
# 安装依赖包
python pip_requirements.py
```

注意：
- 如果是虚拟环境，请先切换至虚拟环境


### 2.3.启动步骤

使用 **python** 以 **模块** 方式启动应用。

- 方式一：自动化脚本启动，用于部署服务阶段

```BASH
# 加载启动配置
source environment.sh
# 添加执行权限
chmod +x start.sh
# 启动程序
./start.sh
```

此时，日志默认存放在 **logs** 目录的 **debug.log** 文件中，查看方式如下：

```BASH
tail -f ./logs/debug.log
```

- 方式二：手动启动，用于代码调试阶段

```BASH
# 加载启动配置
source environment.sh
# 启动程序
python -u -m meeting_assistant.app
```


### 2.4.停止步骤

使用自动化的脚本停止

```BASH
# 添加执行权限
chmod +x stop.sh
# 停止程序
./stop.sh
```


### 2.5.重启步骤

使用自动化的脚本重启

```BASH
# 添加执行权限
chmod +x restart.sh
# 重启程序
./restart.sh
```


## 3.开发说明


### 3.1.路由（router）编写

在编写路由时，在 **routers** 目录注册路由，具体在 **services** 目录下编写实现。文件命名方式采用 **xxx_router.py** 和 **xxx_service.py**。

- 首先，在 **routers** 目录下编写子路由逻辑，变量命名统一为 **router = APIRouter()**

```PYTHON
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def do_get_hello_world():
    return "Hello World!"
```

- 其次，在 **app.py** 引入子路由

```PYTHON
from .routers import hello_world_router

app.include_router(hello_world_router.router)
```


### 3.2.请求（request）与响应（response）编写

使用 **pydantic** 对请求与响应做强制校验时，建议在 **items** 目录下编写实现。文件命名方式采用 **xxx_item.py**。


### 3.3.数据库表（model）编写

使用 **sqlalchemy orm** 实现数据表映射，建议在 **models** 目录下编写实现，请继承 **BaseModel** 基类。文件命名方式采用 **xxx_model.py**。

- 注意：
  - id 必须使用 uuid4，禁止使用 **自增 id**。


### 3.4.设置项（setting）与配置项（config）编写

在编写模块中常用的设置项与配置项时，建议在 **settings** 目录下编写实现。文件命名方式采用 **xxx_config.py**。

在引用时，请引用文件名，**不要直接引用**。

- 正确

```PYTHON
from .settings import file_config, environment_config

def run_as_https_server():
    """以 https 单向认证启动服务。"""
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=environment_config.HOST,
        port=environment_config.PORT,
        reload=environment_config.RELOAD,
        workers=environment_config.WORKERS,
        ssl_keyfile=file_config.CONST_SERVER_PRIVATE_KEY,
        ssl_certfile=file_config.CONST_SERVER_CERTIFICATE,
    )
```

- 错误

```PYTHON
from .settings.environment_config import HOST, PORT, RELOAD, WORKERS
from .settings.file_config import CONST_SERVER_PRIVATE_KEY, CONST_SERVER_CERTIFICATE

def run_as_https_server():
    """以 https 单向认证启动服务。"""
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        workers=WORKERS,
        ssl_keyfile=CONST_SERVER_PRIVATE_KEY,
        ssl_certfile=CONST_SERVER_CERTIFICATE,
    )
```


### 3.5.命令行工具类（tool）编写

在 **tools** 目录实现命令行工具，模板中已经实现 **command_tool.py** 基本工具，支持上下查看历史、回车自动补全。

在具体实现时调用，通过 Command 类，添加命令执行函数。

```PYTHON
command = Command()
command.add_function(find_and_load_models)
command.add_function(create_tables)
command.add_function(drop_tables)
command.add_function(show_tables)
command.run()
```


### 3.6.公用工具类（util）编写

建议在 **utils** 目录下编写实现。文件命名方式采用 **xxx_util.py**。

在引用时，请引用文件名，**不要直接引用**。

- 正确

```PYTHON
from .utils import log_util

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 开始
    log_util.set_log(debug=True)
    yield
    # 结束
```

- 错误

```PYTHON
from .utils.log_util import set_log

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 开始
    set_log(debug=True)
    yield
    # 结束
```


### 3.7.Depends 写法

在使用 **Depends** 时，请使用以下写法：

- 正确

```PYTHON
def login(login_items: dict, db: Session = Depends(get_db))
```

- 错误

```PYTHON
from typing_extensions import Annotated
def login(login_items: dict, db: Annotated[Session, Depends(get_db)])
```

- 注意：
    - get_db 函数不能使用 **yield** 关键字返回数据


### 3.8.测试（test）编写

建议在 **tests** 目录下编写实现。文件命名方式采用 **test_xxx.py**。


## 4.编译说明

对外部署时，需要进行 **代码编译**，实现保护 **知识产权**。

使用时，请执行：

```BASH
# 添加执行权限
chmod +x compile.sh
# 编译
./compile.sh
```

编译完成后，编译结果保存在 **builds** 目录。

**compile.sh** 总体思路分两个步骤：
- 第一步，使用 **cython** 将所有代码编译成 **xxx.so** 或 **xxx.pyd**，分别对应 linux 平台和 windows 平台
- 第二步，使用 **pyinstaller** 将所有 **xxx.so** 或 **xxx.pyc** 打包成可执行文件 **xxx** 或 **xxx.exe**

基于上述想法，设计整个流程自动化脚本，接下来详细介绍实现过程。


### 4.1.Cython 编译

- 执行命令

```BASH
######## 编译为 pyd 或者 so ########
# 执行 cython 编译
python cython_setup.py
```

首先，通过 **list_pythons** 函数，获取模块中所有的 **python** 代码。

```PYTHON
python_list = list_pythons()
```

然后，执行编译命令，指定参数 **ext_modules**、**script_args**、**options** 和 **cmdclass**。

```PYTHON
# 编译所有 py 文件
setup(
    name=PACKAGE_NAME,  # 模块名称
    ext_modules=cythonize(
        python_list,
        nthreads=os.cpu_count(),
    ),  # 待编译 python 文件列表
    script_args=[
        "build_ext",
        "--inplace",
        f"--parallel={os.cpu_count()}",
    ],  # 保证 build 运行后，会执行 copy_extensions_to_source
    options={
        "build_ext": {
            "build_temp": "builds",  # build 临时目录
            "build_lib": "builds",  # build 保存目录
        },
    },
    cmdclass={
        "build_ext": CustomBuildExt,  # build 执行类
    },
)
```


#### 4.1.1.CustomBuildExt 设计详细

**CustomBuildExt** 是指定的编译执行类，用于记录编译信息，并在编译完成后，清理编译冗余信息。

- 首先，在 **build_extensions** 函数中，增加编译优化信息，实现对编译的精准控制

注意：区别不同的平台

```PYTHON
def build_extensions(self):
    """构建编译命令。"""
    for extension in self.extensions:
        if sys.platform.startswith("linux"):
            self.build_linux_extension(extension)
        elif sys.platform.startswith("win"):
            self.build_windows_extension(extension)
        else:
            raise Exception(f"unknow platform {sys.platform}")

    super().build_extensions()
```

- 其次，在 **get_ext_filename** 函数中，移除编译后的文件中包含的 **平台特定信息**

```PYTHON
def get_ext_filename(self, full_name):
    """构建编译后文件名。"""
    # 获取默认的扩展文件名
    full_name = super().get_ext_filename(full_name)

    # 移除平台特定信息
    # linux 平台：xxx.cpython-38-x86_64-linux-gnu.so
    # windows 平台：xxx.cp313-win_amd64.pyd
    full_name_splits = full_name.split(".")
    assert len(full_name_splits) == 3
    full_name = f"{full_name_splits[0]}.{full_name_splits[2]}"
    return full_name
```

- 最后，在 **copy_extensions_to_source** 函数中，实现三个功能

第一个是，删除 **xxx.c** 文件

```PYTHON
# 删除 xxx.c 文件
source_file_list = self.get_source_files()
for source_file in source_file_list:
    if os.path.exists(source_file):
        os.remove(source_file)
```

第二个是，将 **__init__.py** 文件，拷贝至 **build** 目录，并且对编译的 python 文件进行解析，记录 **import**，将结果保存至 **build** 目录的 **hidden_imports.json** 文件中

```PYTHON
# 处理 __init__.py 文件，将其拷贝至 build 目录
current_directory = absolute_directory(__file__)
build_py = self.get_finalized_command("build_py")

import_list_dict = dict()
import_list_dict["default"] = []
for extension in self.extensions:
    # 判断平台
    if sys.platform.startswith("linux"):
        ends = ".so"
    elif sys.platform.startswith("win"):
        ends = ".pyd"
    else:
        raise Exception(f"unknow platform {sys.platform}")

    # inplace_file 编译的源文件
    # regular_file 目的文件
    inplace_file, regular_file = self._get_inplace_equivalent(build_py, extension)

    if regular_file.endswith(f"__init__{ends}"):
        # 重组源文件目录
        inplace_file = inplace_file.replace(ends, ".py")
        inplace_file = os.path.join(current_directory, "..", inplace_file)

        # 重组目标文件目录
        regular_file = regular_file.replace(ends, ".py")
        regular_file = os.path.join(current_directory, regular_file)

        # 执行拷贝
        shutil.copy(inplace_file, regular_file)

    else:
        # 添加编译的模块
        # linux 目录使用 /
        # windows 目录使用 \
        import_list_dict["default"].append(inplace_file.replace(ends, "").replace("/", ".").replace("\\", "."))

        # 记录隐藏的 import
        # 重组源文件目录
        inplace_file = inplace_file.replace(ends, ".py")
        inplace_file = os.path.join(current_directory, "..", inplace_file)

        import_list_dict[inplace_file] = parse_imports(inplace_file)

# 保存隐藏 import
hidden_imports_file_path = os.path.join(current_directory, "builds", "hidden_imports.json")
fw = open(hidden_imports_file_path, "w", encoding="utf-8")
fw.write(json.dumps(import_list_dict, indent=4))
fw.close()
```

第三个是，**注释掉拷贝代码**，禁止将编译结果拷贝至对应的 python 文件目录

```PYTHON
# 禁止拷贝，请勿解除注释
# super().copy_extensions_to_source()
```


### 4.2.PyInstaller 编译

- 执行命令

```BASH
# ######## 编译执行文件 ########
# 进入编译目录
cd "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/builds"

# 执行拷贝脚本
# 注意 cp 通配符展开必须去除 "
cp $ABSOLUTE_SCRIPT_PARENT_DIRECTORY/compile*.py "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/builds/"
cp "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/pyinstaller_setup.py" "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/builds/"

# 执行 pyinstaller 编译
python pyinstaller_setup.py
```

在 pyinstaller 命令中，指定隐藏导入 **hiddenimports**，将资源目录（**statics**，**logs**，**temps**）目录打包至可执行文件中，以及可执行程序的 python 文件 **compile\*.py**。


#### 4.2.1.PyInstaller 脚本详细设计

通过 pyinstaller api，配合 cython 编译过程中输出的 **hidden_imports.json** 实现自动添加隐藏导入，并编译。

下面以编译 ***compile_app** 为例详细介绍。

- 首先，加载隐藏的 import

```PYTHON
# 隐藏 import
PyInstaller.config.CONF["hiddenimports"] = load_hiddenimports()
```

- 其次，拷贝资源数据

```PYTHON
# 拷贝数据目录
data_args = copy_datas()
```

- 最后，执行编译
```PYTHON
# 编译 app
args = data_args + [
    "--onefile",
    f"--name={PACKAGE_NAME}_app",
    "--distpath",
    f"{CURRENT_DIRECTORY}/pyinstaller_dist",
    "--workpath",
    f"{CURRENT_DIRECTORY}/pyinstaller_build",
    "compile_app.py",
]
print(f"args:{args}")

PyInstaller.__main__.run(args)
```


## 5.注意事项

- 在 **Python 开发** 时，请使用 **相对引用**。

- FastApi 使用 **APIRouter** 子路由构建路径。

- 禁止使用 **pathlib** 库，因为 **pyinstaller** 不支持，请使用 **pip uninstall pathlib** 卸载

- 禁止使用 **json.loads** 解析列表（**[]**），所有 json 数据必须是字典（**{}**）

- 禁止在 **@router** 监听函数中直接返回 **await**

错误：

```PYTHON
@router.get("/")
async def do_await():
    return await async_function()
```

正确：

```PYTHON
@router.get("/")
async def do_await():
    return Response(await async_function())
```


## 参考文档

- 官方文档

> https://fastapi.org.cn/learn/

- swagger

> https://github.com/swagger-api/swagger-ui

> https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css

> https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js

> https://fastapi.tiangolo.com/img/favicon.png

