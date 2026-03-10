import time, json
from threading import Thread
from copy import deepcopy
from datetime import datetime as dt
from datetime import timedelta

import paho.mqtt.client as mqtt

from collections import deque

from db import db
from da.DAN import DAN, log
from da.errorlog import errorlog 

from config import CSM_HOST as host
from config import MQTT_broker as broker
from config import MQTT_port as mqt_port
from config import MQTT_User as mqt_usr
from config import MQTT_PW as mqt_pw
from config import MQTT_encryption as mqt_encrypt


CR = '\033[1;32;41m'
CB = '\033[1;33;44m'
R  = '\033[0m'  # RESET COLOR

RUNNING_FIELDS = set()

def _run(profile, reg_addr, field, field_id, alert_range={}):
    dan = DAN()
    dan.device_registration_with_retry(profile, host, reg_addr)
    
    ODF_list = deepcopy(dan.selected_DF)
    ODF_list.remove('Alert-I')

    log_ts_len = 30
    previous_timestamp=[]
    def check_timestamp(timestamp):
        cut_ms = timestamp.split('.')[0]
        ts = dt.strptime(cut_ms, '%Y-%m-%d %H:%M:%S')
        if ts in previous_timestamp:
            if len(previous_timestamp)>log_ts_len: return 'DROPOUT'
            while True:
                ts = ts + timedelta(seconds=1)
                if ts not in previous_timestamp: break
            previous_timestamp.append(ts)
            return str(ts)
        else:
            if len(previous_timestamp)>log_ts_len:
                if ts > previous_timestamp[-1]: previous_timestamp.clear()
            previous_timestamp.append(ts)
            return 0

    data_queue = deque()
    def to_data_queue(q, data):
        q.append(data)
    

    def queue_mgr(db, data_queue, mqtt_client):
        nonlocal DISCONNECT
        while True:
            if DISCONNECT: reconnect(mqtt_client)
            try:
                # 改用 popleft() 取資料，O(1)
                odf, value, ts_str = data_queue.popleft()
            except IndexError:
                # 佇列空才稍微休息，避免忙迴圈；不要每處理一筆都 sleep
                time.sleep(0.001)
                continue
                
            r = check_timestamp(ts_str)     
            if r: 
                if r == 'DROPOUT': 
                    print('{}{}: Extended timestamp list is full. Data dropped.{}'.format(CR, field, R))
                    continue
                ts_str = r
            insert_into_db(db, odf, value, ts_str)

    def reconnect(client):
        client.disconnect()
        client.loop_stop()
        time.sleep(0.5)
        print('[{}] MQTT reconnect...'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S')))
        while True:
            try:
                client.reconnect()
                break
            except BaseException as err:
                print(err)
        client.loop_start()
        time.sleep(0.5)

    def insert_into_db(db, odf, value, timestamp):
        session = db.get_session()
        try:
            new_value = getattr(db.models, odf.replace('-O', ''))(timestamp=timestamp, field=field_id, value=value)
            session.add(new_value)
            session.commit()
        except Exception as e:
            print('insert_into_db_error:{}->{}'.format(field, str(e)))
            errorlog('insert_into_db_error', reg_addr, field, value, '{}---{}'.format(timestamp, str(e)))
        session.close()  
    

    DISCONNECT = False
    def on_connect(client, userdata, flags, rc):
        nonlocal DISCONNECT
        if not rc:
            if DISCONNECT: DISCONNECT = False
            print('{}[{}]{}: MQTT broker = {}{}'.format(CB, dt.now().strftime('%Y-%m-%d %H:%M:%S'), field, broker, R))
            if ODF_list == []:
                print('ODF_list is not exist. {}: {}'.format(field, reg_addr))
                return
            topic_list=[]
            for odf in ODF_list:
                topic = '{}//{}'.format(reg_addr, odf)
                topic_list.append((topic,0))
            if topic_list != []:
                r = client.subscribe(topic_list)
                if r[0]: print('Failed to subscribe topics. Error code:{}'.format(r))
        else: print('Connect to MQTT borker failed. Error code:{}'.format(rc))

    def on_disconnect(client, userdata,  rc):
        nonlocal DISCONNECT
        print('{}[{}] MQTT disconnected.{}'.format(CR, dt.now().strftime('%Y-%m-%d %H:%M:%S'), R))
        errorlog('Disconnect', reg_addr, field)
        DISCONNECT = True

    def on_message(client, userdata, msg):
        samples = json.loads(msg.payload)
        device_id, ODF_name = msg.topic.split('//')
        ODF_timestamp = samples['samples'][0][0]
        ODF_data = samples['samples'][0][1][0]
        print('[{}] {}, {}, {}, {}'.format((ODF_timestamp.split('.'))[0], field, device_id, ODF_name, ODF_data))
        to_data_queue(data_queue, [ODF_name, ODF_data, ODF_timestamp])
        log.debug(field, ODF_name, ODF_data)
        check_alert(client, device_id, ODF_name, ODF_data)   
       

    def MQTT_config(client, broker, port, user, pw, encryption=False):
        client.username_pw_set(user, pw)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        if encryption: client.tls_set()
        client.connect_async(broker, port, keepalive=60)

    def mqtt_pub(client, deviceId, IDF, data):
        topic = '{}//{}'.format(deviceId, IDF)
        sample = [str(dt.today()), data]
        payload  = json.dumps({'samples':[sample]})
        status = client.publish(topic, payload)
        if status[0]: print('topic:{}, status:{}'.format(topic, status))

    def check_alert(client, device_id, odf, odf_data):
        if odf not in alert_range: return
        alert_min = alert_range[odf].get('min', 0)
        alert_max = alert_range[odf].get('max', 0)
        if alert_min != alert_max and (odf_data > alert_max or odf_data < alert_min):
            if client: mqtt_pub(client, device_id, odf, '{} {}'.format(odf, odf_data))
            else: dan.push('Alert-I', '{} {}'.format(odf, odf_data))
            print('Alert-I: {}, {}, {}'.format(device_id, odf, odf_data))

    if broker:
        mqttc = mqtt.Client()
        MQTT_config(mqttc, broker, mqt_port, mqt_usr, mqt_pw, mqt_encrypt)
        mqttc.loop_start()    
        queue_mgr(db, data_queue, mqttc)
        return
        
    while True:
        try:
            # Pull data
            for df in dan.selected_DF:
                data = dan.pull_with_timestamp(df)
                if data:
                    print('{}: {}, {}'.format(field, df, data))
                    log.debug(field, df, data)
                    timestamp = data[0]
                    try:
                        value = float(data[1][0])
                    except Exception as e:
                        log.warning(e, ', ignore this data.')
                        continue
                    insert_into_db(db, df, value, timestamp)
                    check_alert(None, reg_addr, df, value)
            time.sleep(20)
        except KeyboardInterrupt:
            log.info(field, ': exit')
            break
        except Exception as e:
            log.error('[ERROR]:', e)
            if str(e).find('mac_addr not found:') != -1:
                log.error('Reg_addr is not found. Try to re-register...')
                dan.device_registration_with_retry(profile, host, reg_addr)
            else:
                log.error('Connection failed due to unknow reasons.')
                time.sleep(1)
        finally:
            #session.close()
            pass
            
def _spawn_field_runner(field_row, session):
    """為單一 field 建立 profile/alert_range，並啟動對應的 _run() 執行緒。"""
    global RUNNING_FIELDS, broker

    field = field_row
    profile = {
        'd_name': field.name,
        'dm_name': 'Dashboard',
        'df_list': ['Alert-I'],
        'is_sim': False,
    }
    if broker:
        profile['mqtt_enable'] = True

    alert_range = {}
    query_df = (session.query(db.models.field_sensor)
                      .select_from(db.models.field_sensor)
                      .join(db.models.sensor)
                      .filter(db.models.field_sensor.field == field.id)
                      .all())
    for fs in query_df:
        profile['df_list'].append(fs.df_name)
        alert_range[fs.df_name] = {'min': fs.alert_min, 'max': fs.alert_max}

    if not profile['df_list']:
        return  

    t = Thread(
        target=_run,
        args=(profile, profile['d_name'], field.name, field.id, alert_range),
        daemon=True
    )
    t.start()
    RUNNING_FIELDS.add(field.id)
    time.sleep(0.2)

def _scan_and_spawn_new_fields():
    """掃描 DB，對尚未啟動的 field 補開 _run()。"""
    session = db.get_session()
    try:
        for f in session.query(db.models.field).all():
            if f.id in RUNNING_FIELDS:
                continue
            _spawn_field_runner(f, session)
    finally:
        session.close()

def main(sync_queue=None):
    """
    若 sync_queue 傳進來（server.py 會傳），就用它觸發「增量同步」；
    不再需要 /restart_da，每次 signal 只補新 field 的 _run()。
    """
    db.connect()

    # 先跑一次，把現有 field 都啟動
    _scan_and_spawn_new_fields()

    # 若有 queue，啟動一個背景 worker：每收到 signal 就做一次增量掃描與補開
    if sync_queue is not None:
        def _sync_worker():
            last_ts_by_project = {}  # 簡單 debounce（同專案太頻繁訊號只取最新）
            while True:
                job = sync_queue.get()
                if not isinstance(job, dict):
                    continue
                if job.get('op') != 'sync_project':
                    continue
                pj = job.get('project')
                ts = job.get('ts', 0)
                # 同一 project 只處理較新的
                if pj in last_ts_by_project and ts <= last_ts_by_project[pj]:
                    continue
                last_ts_by_project[pj] = ts

                try:
                    # 這裡不強依賴 schema（不過濾 project），直接做「增量掃描」
                    # 好處是即使你一次建立多個 project 的 field，也能一次補起來
                    _scan_and_spawn_new_fields()
                    print(f"[sync] handled project={pj} at {dt.now().strftime('%H:%M:%S')}")
                except Exception as e:
                    print(f"[sync] error for project={pj}:", e)

        Thread(target=_sync_worker, daemon=True).start()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print('Bye')


if __name__ == "__main__":
    main()
