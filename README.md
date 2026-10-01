生产部署须知（三步轻松无痛上线）：
⭐1.需要修改环境变量(已改好，直接跳过)
 方法1→直接修改D:\travel_hub/backend/config.py,
···将最后一行；`BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000/')改为`：
··`·BASE_URL = os.environ.get('BASE_URL', 'https://fbll.asia/')`
 方法2→通过指令设置生产环境变量：
···`·Windows (CMD):set BASE_URL=https://fbll.asia
····Windows (PowerShell):$env:BASE_URL = "https://fbll.asia"`
⭐2.运行数据库迁移交互命令（确保完成第一步修改BASE_URL）：
··在项目根目录下，激活虚拟环境后运行
`：python migrate_all_urls.py.py `
    试运行后，检查输出结果是否符合预期：检查输出的更新路径是否正确（例如：https://fbll.asia/uploads/cat_20260524_163740.jpg）
点击可正常访问，即代表试运行无误；则实际执行，运行：`python migrate_all_urls.py --commit`数据库已备份，输入yes直接执行程序；
运行成功后会输出：n迁移完成！共更新 {total_updated} 条记录。
（此步操作的意味：用于迁移数据库中原有的使用本地路径储存的数据，脚本会将数据库中的路径改为使用服务器的域名，将 http:// localhost:5000 替换为 fbll.asia）
（**警告**⚠：请不要在生产环境重复执行此脚本，否则会将生产域名替换为 localhost，导致资源失效。）
⭐3.根据下方版本变更声明下载新安装的包↓
⭐4.安全配置：虽然很遗憾，但SECRET_KEY不建议使用默认的 WYHlovezc，改为环境变量（config.py):SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
⭐5.启动后端、前端，上线！
（注：Cors配置已更改，无需您操心，如有错误请联系开发者）
恭喜你成功发射了一个项目！
⭐6. 验证部署
  - 访问 https://fbll.asia
  - 直接进行身份注册、登录
  - 打开主面，确认图片、音乐能正常加载（可多次刷新）
  - 测试主页样式切换
  - 测试音乐播放
  - 测试文件上传功能
  - 检查浏览器控制台无错误
       
主页的精选的优美音乐与精美壁纸将是您最好慰劳
            ——————爱你的开发者 porridge


# ·3.0最终版声明·
截至现在，Travel-Hub三期项目正式开发完毕，开发环境测试完善，希望尽早上线
本版本变更如下：
1.支持添加日志巡游轨迹
2.完善地图系统，及数据资源收集
3.自定义主页样式
较上一版本，后端无新增软件包
前端需安装fontawesome-free图标库，终端运行：
cd frontend
npm install @fortawesome/fontawesome-free
如遇到难以解决的问题，请使用travel_hub/项目架构概要.txt文件，以便向Ai获取帮助时附上该文件方便问题的解决
                                ——————2026.6.8 porridge

# ·2.21测试版声明·

1.试图解决图像渲染与tinyMCE加载问题
2.新增开发者控制页面（Developer Control），方便直接管理与维护
3.完善优化文章系统与用户界面
4.测试出行日志wiki系统
                ——————2026.5.24  porridge



`呈魏贤兄文几`：
   首先，我对您即将开展的我站项目生产环境部署工作、对您不辞辛劳闲暇之余鼎助玉成表示**由衷敬佩和诚挚感激**
   出行交流网站（下皆简称我站）是一个以Flask-Restful+Vue3为基本框架的前后端分离项目。我站项目一期（2025.8~2025~11）现已基本落成，最后于本周成功封顶。
 我认为是时候对本项目进行生产环境的线上部署测试，由于本次项目架构较以往变化较大，项目体积以及与依赖环境空前庞大，所以有必要进行提前的必要准备与部署。
 希望以下步骤能帮助您更快更轻松地完成环境安装

一.后端的环境依赖：
  当前项目依赖环境为Python3.8，所以请确保已安装Python3.8环境。由于引入包较多，建议直接运行[requirements.txt]文件安装主要的依赖包。(..%2Fbackend%2Frequirements.txt)
如有缺少的包请结合报错，参照routes.py中的import 语句进行安装补全。
二.前端环境依赖：
  当前项目依赖环境为Vue3.0，所以请确保已安装Vue3.0环境。
  1.安装Node。首先您需要确保安装了Node.js[下载地址](https://nodejs.cn/download/),或者直接在面板搜索下载(如果有)
  2.安装Vue 可以到官网安装[Vue中文官网](https://cn.vuejs.org/)项目版本为Vue3.5.18安装完成后，可以使用npm install语句安装
  3.安装脚手架：使用npm语句在生产环境中初始化Vue,npm install @vue/cli-service -g
Vue有专门管理环境包的文件，所有依赖在[package.json](package.json)文件中已写好，后续有需要可直接添加如有其他需要，
三.项目的运行
  请先启动后端，预热正常后再运行Vue项目启动前端，**遵循原则：前后端分离、先后再前**
  1.初始化数据库、录入初始数据
  2.启动后端：直接运行app.py，
  3.进入前端目录，运行预启动前端
  构建生产环境目录：运行语句 npm run build
  4.启动前端：运行语句 npm run serve
  使用Node.js服务器（可选）
虽然Vue应用通常可以作为静态文件部署，但在某些情况下，你可能想在Node.js服务器上运行Vue应用（例如，使用Nuxt.js或Vue SSR）。对于这种情况，
npm run serve
 部署过程中碰到难题的地方欢迎垂问，请及时反馈部署进度，遇到问题随时联系，
   Yours            
   谨奉

**#** 如何启动一个Vue项目？（官方）：

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```
——2025.11
