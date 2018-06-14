Berryfolio
==========

![Project status][status]

Project of DigitalAssetsManagement2017@ZJU. 
A simple digital media assets management system handling images with Web GUI and user system.
A zipped file containing portfolio of a single user can be output by this system. 

Table of Contents
-----------------

  * [Requirements](#requirements)
  * [Usage](#usage)
  * [Structure](#structure)
  * [Snapshot](#snapshot)
  * [License](#license)
  * [Contact](#contact)

Requirements
------------

Berryfolio requires the following Python version and Python packages to run:

  * [Python][Python] 2.7
  * [Flask][Flask] 1.0.2
  * [Flask_Uploads][Flask_Uploads] 0.2.1
  * [Flask_wtf][Flask_wtf] 0.14.2
  * [Pillow][Pillow] 5.1.0
  * [WTForms][WTForms] 2.2.1

Usage
-----

Before first run of Berryfolio, you must execute database initialization. Fortunately, I've prepared this script for you.
```cmd
$ cd scripts
$ INIT_DB.cmd
```
Or
```bash
./scripts/INIT_DB.sh
```
if you're using a UNIX OS.

Then you can run the system by executing this:
```cmd
$ cd scripts
$ RUN.bat
```
Done! Now you can open [http://localhost:8080][localhost] for fun!

For more information, please see PDFs under `/documents`

Structure
-------------

```
DAMS
├─berryfolio            // 存放网站源码
│  ├─static             // 存放网站静态文件，包括图标、css、js、包含文件和图片等
│  │  ├─css
│  │  ├─data
│  │  ├─fonts
│  │  ├─icons
│  │  ├─images
│  │  │  ├─avatar
│  │  │  └─generate
│  │  ├─include
│  │  └─scripts
│  ├─templates          // 存放网站网页动态模版（jinja2）
│  └─temp               // 存放用户上传图片、后端制作压缩包等过程中产生的临时文件
├─design                // 存放网站设计稿和静态HTML文件（未使用）
│  └─MyHTML
│      ├─asset
│      │  ├─bootstrap
│      │  │  ├─css
│      │  │  ├─fonts
│      │  │  └─js
│      │  ├─button
│      │  ├─css
│      │  ├─font
│      │  ├─image
│      │  ├─js
│      │  ├─sass
│      │  ├─slide
│      │  └─source
│      ├─img
│      └─js
├─documents
├─scripts               // 存放网站启动和调试脚本、数据库初始化脚本
└─tests                 // 存放后端测试脚本
```

Snapshot
--------
![Home Page][HomePage]  
▲Home Page

![Logged In][LoggedIn]  
▲Logged In

![Sign In][SignIn]  
▲Sign In

![Log In][LogIn]  
▲Log In

![My Page][MyPage]  
▲My Page

![Create Folder][CreateFolder]  
▲Create Folder

![Upload][Upload]  
▲Upload

![Download][Download]  
▲Download

![Update][Update]  
▲Update

![User Info][UserInfo]  
▲User Info

![Search][Search]  
▲Search

License
-------

Berryfolio is licensed under the [MIT][MIT] license 
while all media files related are under [CC BY-NC-ND 4.0][CC BY-NC-ND 4.0].  
Copyright &copy; 2017, [Yunzhe][yunzhe], [Asaki][asaki], [KenBoNely][kenbonely], [Oreki][oreki].

Contact
-------

For any question, please mail to [yunzhe@zju.edu.cn][Mail]



[status]: https://img.shields.io/badge/status-finished-green.svg "Project Status: Finished"

[Python]: https://www.python.org/downloads/
[Flask]: https://github.com/pallets/flask
[Flask_Uploads]: https://github.com/maxcountryman/flask-uploads
[Flask_wtf]: https://github.com/lepture/flask-wtf
[Pillow]: https://github.com/python-pillow/Pillow
[WTForms]: https://github.com/wtforms/wtforms

[localhost]: http://localhost:8080

[HomePage]: documents/HomePage.png "Home Page"
[CreateFolder]: documents/CreateFolder.png "Create Folder"
[Download]: documents/Download.png "Download"
[LoggedIn]: documents/LoggedIn.png "Logged In"
[LogIn]: documents/LogIn.png "Log In"
[MyPage]: documents/MyPage.png "My Page"
[Search]: documents/Search.png "Search"
[SignIn]: documents/SignIn.png "Sign In"
[Update]: documents/Update.png "Update"
[Upload]: documents/Upload.png "Upload"
[UserInfo]: documents/UserInfo.png "User Info"

[MIT]: /LICENCE_MIT.md
[CC BY-NC-ND 4.0]: /LICENCE_CC_BY_NC_ND_4_0.md
[yunzhe]: https://github.com/YunzheZJU
[asaki]: https://gitee.com/AAAAAsaki
[kenbonely]: https://gitee.com/VernierCaliper
[oreki]: https://gitee.com/GamerOreki

[Mail]: mailto:yunzhe@zju.edu.cn