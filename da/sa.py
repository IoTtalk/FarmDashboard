import time
import logging
import re
from datetime import datetime
from db import db
from iottalkpy.dai import module_to_sa
from config import CSM_HOST as host

log = logging.getLogger("\033[1;35m[DA]: \033[0m")


def on_register(dan):
    print('register successfully')


class SaClass:
    def __init__(self, host, field, field_id, profile={}, odf_list=[],
                 alert_range={}, device_addr=None, **kwargs):
        self.host = host
        self.field = field
        self.field_id = field_id
        self.profile = profile
        self.odf_list = odf_list
        self.alert_range = alert_range
        self.device_addr = device_addr
        self.device_name = field.name + '_DataServer'
        self.api_url = host   # get from config CSM_HOST
        self.device_model = 'DataServer'
        self.push_interval = 10
        self.interval = {}
        self.kwargs = kwargs

        for k, v in kwargs.items():
            setattr(self, k, v)

        for odf in odf_list:
            odf = re.sub(r'-', r'_', odf)
            setattr(self, odf, lambda data, odf=odf: self.run(data, odf))

    def run(self, data: list, odf):
        try:
            session = db.get_session()
            if data:
                value = float(data[0])
                odf_class = getattr(db.models, re.sub(r"[-_]O", "", odf))
                new_record = odf_class(timestamp=datetime.now(),
                                       field=self.field_id,
                                       value=value)
                session.add(new_record)
                session.commit()

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


def main():
    db.connect()
    processes = []

    session = db.get_session()

    for field in (session.query(db.models.field).all()):
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
        sa = SaClass(host, field, field.id,
                     profile=profile,
                     odf_list=profile['odf_list'],
                     aler_range=alert_range)

        process = module_to_sa(sa)
        process.daemon = True
        process.start()
        processes.append(process)

    session.close()

    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
