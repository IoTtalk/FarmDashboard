import logging
import re
import time

from config import CSM_HOST
from datetime import datetime
from db import db
from iottalkpy.dai import module_to_sa


log = logging.getLogger("\033[1;35m[DA]: \033[0m")


def on_register(dan):
    print('register successfully')


class SaClass:
    def __init__(self, api_url, field, field_id, d_name, dm_name,
                 odf_list=[], device_addr=None, **kwargs):
        self.api_url = api_url
        self.field = field
        self.field_id = field_id
        self.device_name = d_name
        self.device_model = dm_name
        self.odf_list = odf_list
        self.device_addr = device_addr
        self.push_interval = 10
        self.interval = {}
        self.kwargs = kwargs

        for k, v in kwargs.items():
            setattr(self, k, v)

        for odf in odf_list:
            odf = re.sub(r'-', r'_', odf)
            setattr(self, odf, lambda data, odf=odf: self.on_data(data, odf))

    def on_data(self, data: list, odf):
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
        finally:
            session.close()


def main():
    db.connect()
    processes = []

    session = db.get_session()

    for field in (session.query(db.models.field).all()):
        odf_list = []
        query_df = (session.query(db.models.field_sensor)
                           .select_from(db.models.field_sensor)
                           .filter(db.models.field_sensor.field == field.id)
                           .all())
        for df in query_df:
            odf_list.append(df.df_name)
        sa = SaClass(CSM_HOST, field, field.id,
                     d_name=field.name + '_DataServer',
                     dm_name='DataServer',
                     odf_list=odf_list,)

        process = module_to_sa(sa)
        process.daemon = True
        process.start()
        processes.append(process)

    session.close()

    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
