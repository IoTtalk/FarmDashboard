# FarmDashboard

使用說明：
1. 安裝mysql
2. sudo pip3 install -r requirement.txt   #安裝相關需要套件
3. 修改 config.py，根據內部註解依序填上資料
4. 視情況修改 db_init.json (設定admin密碼與DB初始table欄位)
5. 執行 python3 db.py init
6. 安裝好 tmux
7. 執行 bash startup.sh

至此Dashboard已啟動完成。

*** 注意 ***
在Dashboard上，只要 "新增/修改過Field的項目" 後，就要再次執行 bash startup.sh 更新DA狀態，不然IoTtalk將無法送資料到Dashboard上











