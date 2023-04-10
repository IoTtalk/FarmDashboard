#1.解決duplicate entry，提取device_addr也就是DAI裡的reg_addr, 2.Device name要是field+DataServer, 
#3.將data格式改成(timestamp,data)，使value = data[0][1]成立
import time
import datetime
import logging
import re

from multiprocessing import Process
from db import db
from iottalkpy.dan import Client, DeviceFeature, NoData
from iottalkpy.dai import DAI,module_to_sa
from config import CSM_HOST as host

log = logging.getLogger("\033[1;35m[DA]: \033[0m")  

def on_register(dan):
	print('register successfully')

class SaClass: #將sa的資料變成attribute，讓thread可以帶入到module_to_sa去執行
    def __init__(self, host, field, field_id, profile={}, odf_list=[], alert_range={}, device_addr=None, **args):
        self.host = host
        self.field = field
        self.field_id = field_id
        self.profile = profile
        self.odf_list = odf_list
        self.alert_range = alert_range
        self.device_addr = device_addr   #profile['d_name']
        self.args = args
        self.device_name = field.name + '_DataServer'
        self.api_url = host  #get from config CSM_HOST
        self.device_model = 'DataServer'
        self.push_interval = 10
        self.interval = {'Dummy_Sensor': 3,}
        
    def AvgTD_O(self,data: list):
	    print('df_name: AvgTD_O, data:{}'.format(str(data[0])))
    
    def AvgTemp_O(self,data: list): #df=AvgTemp_O
	    df = 'AvgTemp-O'
	    try:
	        session = db.get_session()
	        if data:
	        	value = float(data[0])
	        	new_model = getattr(db.models, re.sub(r"[-_]O", "", df))(timestamp=datetime.datetime.now(),field=self.field_id, value=value)
	        	session.add(new_model)
	        	session.commit()
	        	
	        	#if df in self.alert_range:
	        	 #   alert_min = self.alert_range[df].get('min', 0)
	        	  #  alert_max = self.alert_range[df].get('max', 0)
	        	   # if alert_min != alert_max and (value > alert_max or value < alert_min):
	        	    #    dan.push('Alert-I', '{} {}'.format(df, value))
    		
	    except KeyboardInterrupt:
	        log.info(self.field, ': exit')
	        	
	    except Exception as e:
		    log.error('[ERROR]:', str(e))
		    if str(e).find('mac_addr not found:') != -1:
		        log.error('Reg_addr is not found. Try to re-register...')
		    else:
		        log.error('Connection failed due to unknow reasons.')
		        time.sleep(1)
	    finally:
	        session.close()	

def main():#執行process
	db.connect()
	processes = []
	
	session = db.get_session()
    
	for field in (session.query(db.models.field).all()): #再外面取完session,field,profile,odf_list後再帶入SaClass
	    profile = {'d_name': field.name + '_DataServer',
	               'dm_name': 'DataServer',
	               'odf_list': [],
	               'is_sim': False}
	    alert_range = {}
	    query_df = (session.query(db.models.field_sensor)
	                       .select_from(db.models.field_sensor)
	                       .join(db.models.sensor)
	                       .filter(db.models.field_sensor.field == field.id)
	                       .all())
	    for df in query_df:
	        profile['odf_list'].append(df.df_name)
	        alert_range[df.df_name] = {'min': df.alert_min,
	                                   'max': df.alert_max}
	    #odf_list = profile['odf_list']
	    #device_addr = profile['d_name']
	    
	    
	    sa = SaClass(host, field, field.id, profile, profile['odf_list'], alert_range, profile['d_name'])
	    
	    process = module_to_sa(sa)
	    process.daemon = True
	    process.start()
	    processes.append(process)
	
	session.close()
	
	for process in processes:
	    process.join()
                                       

if __name__ == "__main__":
    main()
