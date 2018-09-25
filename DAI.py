import time

from threading import Thread

import db

from DAN import DAN
from config import CSM_HOST as host


def _run(profile, reg_addr, field, field_id):
    dan = DAN()
    dan.device_registration_with_retry(profile, host, reg_addr)
    while True:
        try:
            # Pull data
            session = db.get_session()
            for df in dan.selected_DF:
                data = dan.pull_with_timestamp(df)
                if data:
                    print(field, df, data)
                    timestamp = data[0]
                    value = float(data[1][0])
                    new_model = getattr(db.models, df.replace('-O', ''))(timestamp=timestamp, field=field_id, value=value)
                    session.add(new_model)
                    session.commit()
            session.close()
            time.sleep(20)
        except KeyboardInterrupt:
            print(field, ': exit')
            break
            dan.deregister()
        except Exception as e:
            print('[ERROR]:', e)
            continue

def main():
    db.connect()
    threads = []

    session = db.get_session()

    for field in (session.query(db.models.field).all()):
        profile = {'d_name': field.name + '_DataServer',
                   'dm_name': 'DataServer',
                   'df_list': [],
                   'is_sim': False}
        query_df = (session.query(db.models.field_sensor.df_name)
                           .select_from(db.models.field_sensor)
                           .join(db.models.sensor)
                           .filter(db.models.field_sensor.field == field.id)
                           .all())
        for df, in query_df:
            profile['df_list'].append(df)

        thread = Thread(target=_run,
                        args=(profile, profile['d_name'], field.name, field.id))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
