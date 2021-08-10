FarmDashboard
=============

* ~~`詳細安裝說明 <https://hackmd.io/5LqVk4MBSCinRXQderD_Jw>`~~ (此文件已久未更新)

* `Dashboard操作教學影片 <https://drive.google.com/drive/u/1/folders/13AyBQ-3m_RuPOW1J2aR1yD0svUKuEFdg>`_

***Field的名稱不可以包含特如符號如 . $ # & @ 等等，請使用全英文字母***

簡易安裝說明
------------

1. 安裝好 **tmux**：
    ubuntu: 
    ```sh
    apt-get install tmux
    ```
2. 安裝相關需要套件：
    ```sh
    sudo pip3 install -r requirements.txt`` 
    ```
3. (optional) 使用 **MySQL-server**，若不使用可跳過此步並參考下一步的 SQLite 部份。
    * 安裝 MySQL (version >= 5.7) (注意1)
        ```sh
        apt-get install mysql-server
        ```
    * 新增 MySQL 內的 user，允許連線 IP，與資料庫( `db_name` )，以及權限 (注意2)
4. 修改 **config.py**，根據內部註解依序填上資料，主要為設定 DB 路徑
    * 若選擇使用 MySQL：
        依 *注意2* 填 **DB_CONFIG**
    * 若選擇使用 SQLite：
        **DB_CONFIG = 'sqlite+pysqlite:///db.sqlite3'**
5. 修改 **db/db_init.json** (設定 **admin** 密碼)
6. 資料庫初始化：
    ```sh
    python3 -m db.db init
    ```
    * 注意：此步只能執行一次 (只會新加入，並不會抹除舊的資料，所以執行一次以上會錯誤)
    * 在MAC上面使用時可能會遇到加密錯誤的錯誤訊息，這時需要安裝套件 cryptography
8. 啟動 Server：
    ```sh
    bash startup.sh
    ```

至此 Dashboard 已啟動完成，可用指令 ```tmux a``` 查看運行狀況
(按ctrl+b 1 / ctrl+b 2切換 dashboard 主程式與 DA 查看運行狀況)。

### 注意

* 注意1: 安裝mysql時，常會遇到安裝過程中，完全沒問密碼，這表示以前曾經裝過mysql，或是裝過相關套件，這時就比需要重設密碼，執行下列指令進行重設，

    ```sh
    sudo mysqladmin -u root password
    ```
    Reference: https://emn178.pixnet.net/blog/post/87659567

* 注意2: **DB_CONFIG=mysql+pymysql://<user>:<pass>@localhost:3306/<db_name>?charset=utf8**

  其中的 **db_name**，就是打算要建立的資料庫名稱，例如要給 Dashboard 用的，就取名為 ***dashboard***，該主表名稱不是隨便亂輸入的，  通常是在db內建立 user 時，就順道建立一同名的 table，這樣最簡單   (例如，假設使用 phpmyadmin 建立使用者時，就勾選 "建立與使用者同名的資料庫並授予所有權限。")，  權限部分，如果不確定怎麼使用，就全開吧。所以 **db_name** 必須是已存在的資料庫，  而不是隨便亂輸入的。
   
  然後，在建立使用者時，很高的機率會發生錯誤 
  "Your password does not satisfy the current policy requirements"，
  這時要去調降密碼強度限制，解決方法為連上mysql應用，使用如下指令後，  就可以順利建立 user/table 了。

  執行 `mysql -u root -p` 打完密碼後進入 MySQL 命令列，然後執行下方指令::
    ```sql
    mysql> set global validate_password_policy=0;    
    mysql> exit
    ```
  如果是遠端連線，要注意兩點 
  * 要設定該使用者允許連線的 IP，沒去設定的話，絕對是連不上的
  * 記得去掉設定檔內的 `bind 127.0.0.1`


### 多語系使用說明

#### 文字準備

##### python
---

use `gettext('')` to the needing change words.
```python
from flask_babel import gettext
msg = gettext('Babel is good.')
```
or if you want to use constant strings somewhere in your application and define them outside of a request, you can use a lazy strings `lazy_gettext('')`.

```python
from flask_babel import lazy_gettext
msg = lazy_gettext('Babel is good.')
```

##### Javascript
---

use `{{ _('') }}` to the needing change words.

```html
<div class="title">{{ _('System Management') }}</div>
```

#### 使用語言包

* 首次使用

  1. 將所有 python 及 html 所用到的字串頡取出來：
      `pybabel extract -F app/babel.cfg -o messages.pot .`

  2. 建立字典檔 (儲放於 `app/translations` 下)：
      `pybabel init -i messages.pot -d app/translations/ -l <lang_code>`

  3. 翻譯文字，修改前一步產生的 po 檔，翻譯對應語系的文字，檔案路徑為：
      `app/translations/<lang_code>/LC_MESSAGES/messages.po`

  4. 編譯字典 po 檔成 mo 檔，供 babel 使用：
      `pybabel compile -f -d app/translations`

* 更新字典檔 (與首次使用相同，差別在於第二步的 update 用 `update` 取代 `init`)

  1. 將所有 python 及 html 所用到的字串頡取出來：
      `pybabel extract -F app/babel.cfg -o messages.pot .`

  2. 更新字典檔：
      `pybabel update -i messages.pot -d app/translations/ -l <lang_code>`

  3. 翻譯文字，修改前一步產生的 po 檔，翻譯對應語系的文字，檔案路徑為：
      `app/translations/<lang_code>/LC_MESSAGES/messages.po`

  4. 編譯字典 po 檔成 mo 檔，供 babel 使用：
      `pybabel compile -f -d app/translations`