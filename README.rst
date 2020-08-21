=============
FarmDashboard
=============

**Field的名稱不可以包含特如符號如 . $ # & @ 等等，請使用全英文字母**

********
Overview
********

`Dashboard操作教學影片 <https://drive.google.com/drive/u/1/folders/13AyBQ-3m_RuPOW1J2aR1yD0svUKuEFdg>`_

data diagram
============
https://i.imgur.com/AU8Oqrf.jpg 


dataflow
================
1. Sensor 的資料透過其 DA 的 IDF 送進 IoTtalk Server。  
2. FarmDashboard 的 DA 藉由 ODF 將資料從 IoTtalk Server 拉下來寫入 Database (e.g. MySQL)中 。
3. Dashboard GUI 會定期去 Dashboard Server 取資料顯示在 GUI 上。

************
Installation
************

| 此手冊適用於 **ubuntu 16.04** 及 **ubuntu 18.04** (`如何安裝 Ubuntu Server <https://tutorials.ubuntu.com/tutorial/tutorial-install-ubuntu-server#0>`_)
| 在 Ubuntu 系統下可輸入指令查看系統版本

::

    $ cat /etc/os-release

| 此手冊以 **MySQL** 作做 Database 所撰寫

Install Environment
===================
python3 and pip3
----------------
::

    $ sudo apt-get install -y python3 python3-pip

git
---
::

    $ sudo apt-get install -y git-core

tmux
----
::
    
    $ sudo apt-get install -y tmux

mysql-server
------------
::

    $ sudo apt-get install mysql-server

| NOTE: password setting:輸入自訂密碼(8位以上) (e.g userpassword)

安全性設定
^^^^^^^^^^

    `操作參考 <https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-ubuntu-16-04#step-2-install-mysql>`_

    ::

        $ mysql_secure_installation

編碼設定
^^^^^^^^
因為會使用中文字儲存，故需將 MySQL 的編碼設定為 utf-8，以避免亂碼。

#. 編輯 MySQL 設定檔 ``/etc/mysql/my.cnf``
    `vim 教學 <https://blog.techbridge.cc/2020/04/06/how-to-use-vim-as-an-editor-tutorial/>`_

#. 插入下列文字
    ::

        [mysqld]
        init_connect = 'SET collation_connection = utf8_bin'
        init_connect = 'SET NAMES utf8'
        character-set-server = utf8
        collation-server = utf8_bin

#. 儲存設定檔並離開
#. 重啟 MySQL 以更新設定
    ::

        sudo service mysql restart
#. 登入 MySQL，確認編碼完成修改

    * 登入 MySQL (以 root 使用者登入)
        ::

            $ mysql -u root -p
    * 檢查系統狀態
        ::

            mysql> status
    * 編碼如下圖即完成設定

    .. image:: https://i.imgur.com/4P5Dobl.png

    * 離開 MySQL
        ::

            mysql> exit

新增使用者
^^^^^^^^^^
在登入 MySQL 後輸入下列指令
::

    CREATE USER '<username>'@'<location>' IDENTIFIED BY '<password>';

| username: 使用者名稱
| location: 允許登入的主機位置，使用 ``%`` 為允許任意位置
| password: 使用者密碼

範例 (使用者名稱及密碼請自行替換):
::
    
    mysql> CREATE USER 'jackthedog'@'%' IDENTIFIED BY 'adventure';

新增 database
^^^^^^^^^^^^^
在登入 MySQL 後輸入下列指令
::

    mysql> create database <db_name>;

| db_name: 建立的資料庫名稱

範列 (資料庫名稱請自行替換)：
::

    mysql> create database treasure;

設定使用者權限
^^^^^^^^^^^^^^
設定剛剛 新使用者 有操作 新資料庫 的權限，在登入 MySQL 後輸入下列指令。
::

    mysql> GRANT <privieges> ON <database>[.<table>] TO '<username>'@'<location>';

| privileges: 使用者操作權限 (`ref <https://dev.mysql.com/doc/refman/5.7/en/privileges-provided.html>`_)，使用 ``ALL PRIVILEGES`` 為所有權限。
| database: 可操作的資料庫，使用 ``*`` 為所有資料庫
| table: 可操作的資料表，使用 ``*`` 為所有表
| username: 欲修改權限的使用者
| location: 允許從何處登入的權限

範例 (各欄位請自行替換):
::

    mysql> GRANT ALL PRIVILEGES ON *.* TO 'jackthedog'@'%';

更新權限設定
^^^^^^^^^^^^
將剛剛設定完的權限啟用，在登入 MySQL 後輸入下列指令。
::

    mysql> flush privileges;



簡易安裝說明
----------------------------------------------------------------------

#. 安裝 MySQL >= 5.7 (注意1)
#. ``sudo pip3 install -r requirements.txt`` 安裝相關需要套件
#. 新增 MySQL 內的 user，允許連線 IP，與資料庫( `db_name` )，以及權限 (詳見下方注意2)
#. 修改 `config.py`，根據內部註解依序填上資料
#. 視情況修改 `db_init.json` (記得要設定 `admin` 密碼與 DB 初始 table 欄位)
#. 執行 ``python3 db.py init``  (注意3)
#. 安裝好 ``tmux``
#. 執行 ``bash startup.sh``  (注意4)

至此 Dashboard 已啟動完成，可用指令 ``tmux a`` 查看運行狀況
(按ctrl+b 1 / ctrl+b 2切換 dashboard 主程式與 DA 查看運行狀況)。




注意
----------------------------------------------------------------------

- ***注意1***: 安裝mysql時，常會遇到安裝過程中，完全沒問密碼，這表示以前曾經裝過mysql，或是裝過相關套件，這時就比需要重設密碼，執行下列指令進行重設，

    sudo mysqladmin -u root password

  Reference: https://emn178.pixnet.net/blog/post/87659567


- ***注意2***: ``mysql+pymysql://<user>:<pass>@localhost:3306/<db_name>?charset=utf8``
  其中的 ``db_name``，就是打算要建立的資料庫名稱，
  例如要給 Dashboard 用的，就取名為 ``dashboard``，該主表名稱不是隨便亂輸入的，
  通常是在db內建立 user 時，就順道建立一同名的 table，這樣最簡單
  (例如，假設使用 phpmyadmin 建立使用者時，就勾選 "建立與使用者同名的資料庫並授予所有權限。")，
  權限部分，如果不確定怎麼使用，就全開吧。所以 ``db_name`` 必須是已存在的資料庫，
  而不是隨便亂輸入的。
   
  然後，在建立使用者時，很高的機率會發生錯誤 
  "Your password does not satisfy the current policy requirements"，
  這時要去調降密碼強度限制，解決方法為連上mysql應用，使用如下指令後，
  就可以順利建立 user/table 了。

  執行 ``mysql -u root -p`` 打完密碼後進入 MySQL 命令列，然後執行下方指令::

        mysql> set global validate_password_policy=0;    
        mysql> exit
- 如果是遠端連線，要注意兩點 
    #. 要設定該使用者允許連線的 IP，沒去設定的話，絕對是連不上的
    #. 記得去掉設定檔內的 ``bind 127.0.0.1``

- ***注意3***: 然後要注意一下， ``python3 db.py init`` 只能執行一次。 (只會新加入，並不會抹除舊的資料，所以執行一次以上會錯誤)
  在MAC上面直接使用，在運行 ``python3 db.py init`` 時可能會遇到加密錯誤的錯誤訊息，這時需要安裝套件 cryptography


- ***注意4***: 在 Dashboard 上，只要 "新增/修改過 Field 的項目" 後，
  就要再次執行 ``bash startup.sh`` 更新 ``DA`` 狀態，
  不然 IoTtalk 將無法送資料到 Dashboard 上




padding
^^^^^^^^^^^^^^^^^^^^^
4. 經由config動作
    * Dashboard GUI 知道要顯示哪些資料
    * DA 知道要去讀取哪些 ODF 以將資料存入mysql。

Sensor設定與連接包含兩個步驟:

1. 在Dashboard上做sensor的設定。(有哪些sensor要讀取)
2. 在IoTtalk Server上建立對應的ODF module。


先選定兩台VM:

* VM1用途:IoTtalk server
* VM2用途:dashboard+mysql
* 先請資訊中心明樺先生開啟VM2的7788port   