# FarmDashboard

使用說明：
1. 安裝mysql
2. sudo pip3 install -r requirements.txt   #安裝相關需要套件
3. 修改 config.py，根據內部註解依序填上資料
4. 視情況修改 db_init.json (設定admin密碼與DB初始table欄位)
5. 執行 python3 db.py init
6. 安裝好 tmux
7. 執行 bash startup.sh

至此Dashboard已啟動完成。

*** 注意 ***
1. 在Dashboard上，只要 "新增/修改過Field的項目" 後，就要再次執行 bash startup.sh 更新DA狀態，不然IoTtalk將無法送資料到Dashboard上

2. 'mysql+pymysql://user:pass@localhost:3306/db_name?charset=utf8'   <--- 其中的 db_name，就是打算要建立的主表名稱，例如要給Dashboard用的，就取名為dashboard，該主表名稱不是隨便亂輸入的，通常是在db內建立user時，就順道建立一同名的table，這樣最簡單(例如，假設使用phpmyadmin建立使用者時，就勾選 "建立與使用者同名的資料庫並授予所有權限。")，權限部分，如果不確定怎麼使用，就全開吧。所以db_name必須是已存在的table，而不是隨便亂輸入的。

3. 如果是遠程連線，要注意兩點 a.要設定該使用者允許連線的IP，沒去設定的話，絕對是連不上的  b.記得去掉設定檔內的 bind 127.0.0.1

4. 然後要注意一下，python3 db.py init 只能執行一次。 (只會新加入，並不會抹除舊的資料，所以執行一次以上會錯誤)
















