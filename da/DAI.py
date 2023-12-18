import time, json
from threading import Thread
from copy import deepcopy
from datetime import datetime as dt
from datetime import timedelta

import paho.mqtt.client as mqtt

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

    data_queue = []
    def to_data_queue(data_queue, data):
        data_queue.append(data)  #data = [ODF_name, ODF_data, ODF_timestamp]

    def queue_mgr(db, data_queue):
        while True:
            if len(data_queue)<1: 
                time.sleep(0.5)
                continue
            data = data_queue.pop(0)
            r = check_timestamp(data[2])        
            if r: 
                if r == 'DROPOUT': 
                    print('{}{}: Extended timestamp list is full. Data dropped.{}'.format(CR, field, R))
                    continue
                data[2]=r
            insert_into_db(db, data[0], data[1], data[2])


    def insert_into_db(db, odf, value, timestamp):
        session = db.get_session()
        try:
            new_value = getattr(db.models, odf.replace('-O', ''))(timestamp=timestamp, field=field_id, value=value)
            session.add(new_value)
            session.commit()
        except Exception as e:
            print('insert_into_db_error:{}->{}'.format(field, str(e)))
            errorlog('insert_into_db_error', reg_addr, field, data[0], '{}---{}'.format(timestamp, str(e)))
        session.close()

    def on_connect(client, userdata, flags, rc):
        if not rc:
            print('{}{}: MQTT broker = {}{}'.format(CB, field, broker, R))
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
        print('MQTT Disconnected. Re-connect...')
        errorlog('Disconnect', reg_addr, field)
        client.reconnect()

    def on_message(client, userdata, msg):
        samples = json.loads(msg.payload)
        device_id, ODF_name = msg.topic.split('//')
        ODF_timestamp = samples['samples'][0][0]
        ODF_data = samples['samples'][0][1][0]
        print('{}: {}, {}, {}, {}'.format(ODF_timestamp, field, device_id, ODF_name, ODF_data))
        #to_data_queue(data_queue, [ODF_name, ODF_data, ODF_timestamp])
        to_data_queue(data_queue, [ODF_name, ODF_data, str(dt.today())])
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
        queue_mgr(db, data_queue)

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
                    insert_into_db(df, value, timestamp)
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
            session.close()

def main():
    db.connect()
    threads = []

    session = db.get_session()

    for field in (session.query(db.models.field).all()):
        profile = {'d_name': field.name + '_DataServer',
                   'dm_name': 'DataServer',
                   'df_list': ['Alert-I'],
                   'is_sim': False}
        if broker: profile['mqtt_enable'] = True
        alert_range = {}
        query_df = (session.query(db.models.field_sensor)
                           .select_from(db.models.field_sensor)
                           .join(db.models.sensor)
                           .filter(db.models.field_sensor.field == field.id)
                           .all())
        for df in query_df:
            profile['df_list'].append(df.df_name)
            alert_range[df.df_name] = {'min': df.alert_min,
                                       'max': df.alert_max}

        if not profile['df_list']:
            continue

        thread = Thread(target=_run,
                        args=(profile,
                              profile['d_name'],
                              field.name,
                              field.id,
                              alert_range))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(2)

    session.close()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
