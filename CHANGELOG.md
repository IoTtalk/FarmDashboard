# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2023-04-20

### Added

- 讓使用者自定要使用V1版本還是V2版本
- 在`config.py`裡新增常數`IOTTALK_VERSION=1`(#0a21efd)

### Changed

- update `server.py`，判斷IOTTALK_VERSION是1還是2，1的話啟動`da/DAI.py`，2的話啟動`da/app.py` (#eac7f6f)

## 2023-04-18

### Changed

- update `app/api.py`，修改tablename的命名方式，只刪除-O，不刪後面的數字 (#14b45a9)

## 2023-04-14

### Changed

- update `requirements.txt`，載入iottalk-py module (#51a8e0f)

## 2023-04-12

### Changed

- update `da/app.py`，改成動態產生以當前odf_name為名的odf_function，讓`v2/dai/on_data`可以執行 (#a2fe8a6)

## 2023-04-10

### Added

- 新增IoTtalk-v2可使用的sa `da/app0330.py`，但還沒加上動態產生odf_function的功能 (#9ab73b1)


### Changed

- update`server.py` ，改成啟動`da/app.py`(#ba17e43)
- rename `app0330.py` to `app.py` (#e145710)



## Rule
每一個軟體的版本必須：
* 標明日期（要用上面說過的規範）
* 標明分類（採用英文）。規範如下：
'Added' 添加的新功能
'Changed' 功能變更
'Deprecated' 不建議使用，未來會刪掉
'Removed' 之前不建議使用的功能，這次真的刪掉了
'Fixed' 修正的 bug
'Security' 修正了安全相關的 bug
