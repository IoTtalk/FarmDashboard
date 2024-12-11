import inspect
import json
import logging
import re

from datetime import datetime
from dateutil import parser

from flask import Blueprint, abort, jsonify, g, redirect, request, session
from sqlalchemy import text, or_
from werkzeug.security import check_password_hash, generate_password_hash

import config

from . import utils
from db import db

log = logging.getLogger("\033[1;33m[API]: \033[0m")
api = Blueprint('API', __name__)


@api.route('/datas/<string:field>', methods=['GET'])
@utils.required_login
def api_query_all_data(field):
    stime = datetime.now()

    res = {}

    start = request.args.get('start')
    end = request.args.get('end')
    limit = int(request.args.get('limit', config.QUERY_LIMIT))

    if start and end:
        start = parser.parse(start)
        end = parser.parse(end)

    query_df = (g.session
                 .query(db.models.field_sensor.df_name,
                        db.models.field_sensor.field)
                 .select_from(db.models.field_sensor)
                 .join(db.models.sensor)
                 .join(db.models.field)
                 .filter(db.models.field.name == field)
                 .all())

    for df_name, field_id in query_df:
        tablename = df_name.replace('-O', '')
        table = getattr(db.models, tablename)
        query = g.session.query(table).filter(table.field == field_id)
        if start and end:
            query = query.filter(table.timestamp >= start, table.timestamp <= end)
        query = query.order_by(table.timestamp.desc()).limit(limit).all()

        res.update({df_name: [(str(record.timestamp), record.value) for record in query]})

    etime = datetime.now()
    log.debug((etime - stime).total_seconds())
    return jsonify(res)


@api.route('/datas/<string:field>/<string:df_name>', methods=['GET'])
@utils.required_login
def api_query_field_data(field, df_name):
    stime = datetime.now()

    tablename = df_name.replace('-O', '')
    if not hasattr(db.models, tablename):
        abort(404)
    table = getattr(db.models, tablename)

    start = request.args.get('start')
    end = request.args.get('end')
    limit = int(request.args.get('limit', config.QUERY_LIMIT))

    if start and end:
        start = parser.parse(start)
        end = parser.parse(end)

    query = (g.session
              .query(table)
              .select_from(table)
              .join(db.models.field)
              .filter(db.models.field.name == field))
    if start and end:
        query = query.filter(table.timestamp >= start, table.timestamp <= end)
    query = query.order_by(table.timestamp.desc()).limit(limit).all()

    res = {df_name: [(str(record.timestamp), record.value) for record in query]}

    etime = datetime.now()
    log.debug((etime - stime).total_seconds())
    return jsonify(res)


@api.route('/datas', methods=['GET'])
@utils.required_login
def api_datas():
    '''
    :args f1: field, like `flower`, `orange`, etc
    :args f2: field, like `flower`, `orange`, etc
    :args s1: sensor, like `AtPressure`, `UV1`, etc
    :args s2: sensor, like `AtPressure`, `UV1`, etc
    :args st: start_time, any time format
    :args et: end_time, any time format
    :args i: interval, only allow `second`, `minute`, `hour`, `day`, default `hour`
    :args l: limit, query limit, default config.QUERY_LIMIT

    example:
        http://your.domain/api/datas?f1=flower&f2=orange&s1=Temperature&s2=AtPressure&st=2018-06-26&et=2018-06-27&i=second
    '''
    stime = datetime.now()

    field1 = request.args.get('f1')
    sensor1 = request.args.get('s1')
    start_time = request.args.get('st')
    end_time = request.args.get('et')
    interval = request.args.get('i', 'hour')
    limit = int(request.args.get('l')) if request.args.get('l') else None

    if not field1 or not sensor1 or not start_time or not end_time:
        abort(404)

    tablename1 = sensor1.replace('-O', '')
    if not hasattr(db.models, tablename1):
        abort(404)

    table1 = getattr(db.models, tablename1)
    start = parser.parse(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end = parser.parse(end_time).strftime('%Y-%m-%d %H:%M:%S')

    result = {sensor1: {}}

    data1 = _query_data(interval, table1.__tablename__, field1, start, end, limit)
    result[sensor1].update({field1: data1})

    field2 = request.args.get('f2')
    if field2:
        sensor2 = request.args.get('s2')
        tablename2 = sensor2.replace('-O', '')
        table2 = getattr(db.models, tablename2)
        if not result.get(sensor2):
            result[sensor2] = {}
        data2 = _query_data(interval, table2.__tablename__, field2, start, end, limit)
        result[sensor2].update({field2: data2})

    etime = datetime.now()
    log.debug((etime - stime).total_seconds())
    return jsonify(result)


@api.route('/export_datas', methods=['GET'])
@utils.required_login
def api_export_datas():
    '''
    :args f: field, like `flower`, `orange`, etc
    :args s: sensor, like `AtPressure`, `UV1`, etc
    :args st: start_time, any time format
    :args et: end_time, any time format
    :args i: interval, only allow `second`, `minute`, `hour`, `day`, default `hour`
    :args l: limit, query limit, default config.QUERY_LIMIT

    example:
        http://your.domain/api/export_datas?f=flower&s=Temperature&st=2018-06-26&et=2018-06-27&i=second
    '''
    stime = datetime.now()

    field = request.args.get('f')
    sensor = request.args.get('s')
    start_time = request.args.get('st')
    end_time = request.args.get('et')
    interval = request.args.get('i', 'hour')
    limit = int(request.args.get('l')) if request.args.get('l') else None

    if not field or not sensor or not start_time or not end_time:
        abort(404)

    tablename = sensor.replace('-O', '')
    if not hasattr(db.models, tablename):
        abort(404)

    table = getattr(db.models, tablename)
    start = parser.parse(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end = parser.parse(end_time).strftime('%Y-%m-%d %H:%M:%S')

    raw_data = _query_data(interval, table.__tablename__, field, start, end, limit)

    content = 'datetime,value\n'

    for data in raw_data[::-1]:
        if interval == 'second':
            content += '{},{}\n'.format(data['timestamp'],
                                        data['value'])
        elif interval == 'minute':
            content += '{} {}:{}:00,{}\n'.format(data['date'],
                                                 data['hour'],
                                                 data['minute'],
                                                 data['value'])
        elif interval == 'hour':
            content += '{} {}:00:00,{}\n'.format(data['date'],
                                                 data['hour'],
                                                 data['value'])
        elif interval == 'day':
            content += '{} 00:00:00,{}\n'.format(data['date'],
                                                 data['value'])
    etime = datetime.now()
    log.debug((etime - stime).total_seconds())
    return content


def _query_data(interval, table_name, field, start, end, limit):
    raw_sql = _get_mysql_raw_sql(interval, table_name, field, start, end, limit)
    query = g.session.execute(raw_sql).fetchall()

    datas = []
    for row in query:
        data = {}
        for key in row.keys():
            data[key] = str(row[key])
        datas.append(data)

    return datas


def _get_mysql_raw_sql(interval, table_name, field, start, end, limit):
    if interval == 'second':
        raw_sql = text('''
            SELECT sensor.timestamp, sensor.value
            FROM {} as sensor
            LEFT JOIN field on field.id = sensor.field
            WHERE field.name = '{}' and
                  sensor.timestamp >= '{}' and
                  sensor.timestamp <= '{}'
            ORDER BY sensor.timestamp DESC
        '''.format(table_name, field, start, end))
    elif interval == 'minute':
        raw_sql = text('''
            SELECT MINUTE(sensor.timestamp) as minute,
                   HOUR(sensor.timestamp) AS hour,
                   DATE(sensor.timestamp) AS date,
                   AVG(sensor.value) AS value
            FROM {} as sensor
            LEFT JOIN field on field.id = sensor.field
            WHERE field.name = '{}' and
                  sensor.timestamp >= '{}' and
                  sensor.timestamp <= '{}'
            GROUP BY minute, hour, date
            ORDER BY date DESC, hour DESC, minute DESC
        '''.format(table_name, field, start, end))
    elif interval == 'hour':
        raw_sql = text('''
            SELECT HOUR(sensor.timestamp) AS hour,
                   DATE(sensor.timestamp) AS date,
                   AVG(sensor.value) AS value
            FROM {} as sensor
            LEFT JOIN field on field.id = sensor.field
            WHERE field.name = '{}' and
                  sensor.timestamp >= '{}' and
                  sensor.timestamp <= '{}'
            GROUP BY hour, date
            ORDER BY date DESC, hour DESC
        '''.format(table_name, field, start, end))
    elif interval == 'day':
        raw_sql = text('''
            SELECT DATE(sensor.timestamp) AS date,
                   AVG(sensor.value) AS value
            FROM {} as sensor
            LEFT JOIN field on field.id = sensor.field
            WHERE field.name = '{}' and
                  sensor.timestamp >= '{}' and
                  sensor.timestamp <= '{}'
            GROUP BY date
            ORDER BY date DESC
        '''.format(table_name, field, start, end))
    else:
        abort(404)

    if limit:
        raw_sql += 'LIMIT {}'.format(limit)

    return raw_sql


@api.route('/user/pwd', methods=['POST'])
@utils.required_login
def api_user_change_pwd():
    user_id = session.get('id')
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')

    if not new_password:
        return 'new password should be given.', 404
    elif old_password == new_password:
        return 'New password can not be identical to the original one', 404
    elif len(new_password) < 6:
        return 'Password length must be greater than or equal to 6', 404
    elif not utils.validate_password_combination(new_password):
        return 'Password must contain at least three of them: Uppercase letters, ' \
               'Lowercase letters, numbers and special symbols', 404

    user = g.session.query(db.models.user).filter(db.models.user.id == user_id).first()

    if not user:
        return 'Who are you?', 404

    if not check_password_hash(user.password, old_password):
        return 'Old passwrod not match.', 404

    user.password = generate_password_hash(new_password)
    g.session.commit()

    return 'ok'


@api.route('/user/delete', methods=['POST'])
@utils.required_login
def api_user_delete_account():
    user_id = session.get('id')
    username = request.json.get('username')
    password = request.json.get('password')

    if not password:
        return 'Password should be given.', 404

    user = g.session.query(db.models.user).filter(db.models.user.id == user_id).first()

    if not user:
        return 'Who are you?', 404

    if user.username != username:
        return 'username not match', 404

    if not check_password_hash(user.password, password):
        return 'Passwrod not match.', 404

    g.session.query(db.models.user_access).filter(db.models.user_access.user == user_id).delete()
    g.session.query(db.models.user).filter(db.models.user.id == user_id).delete()
    g.session.commit()

    if session.get('username'):
        del session['username']

    if session.get('id'):
        del session['id']

    if session.get('is_superuser'):
        del session['is_superuser']

    return redirect('/')
    return 'ok'


@api.route('/user/memo', methods=['POST'])
@utils.required_login
def api_user_update_memo():
    if request.method != 'POST':
        abort(404)

    user_id = session.get('id')
    if not user_id:
        abort(404)

    memo = request.json.get('memo')
    g.session.query(db.models.user).filter(db.models.user.id == user_id).update({'memo': memo})
    g.session.commit()

    return 'ok'


@api.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
@utils.required_superuser
def api_user():
    if request.method == 'GET':
        # Read user
        # GET /api/user[?id=<id>&username=<username>]
        users = []

        query = g.session.query(db.models.user)
        for key, value in request.args.items():
            attr = getattr(db.models.user, key, None)
            if attr:
                query = query.filter(attr == value)
        query = query.order_by(db.models.user.id).all()

        for user in query:
            query_access = (g.session
                             .query(db.models.field, db.models.user_access)
                             .select_from(db.models.user_access)
                             .join(db.models.field)
                             .filter(db.models.user_access.user == user.id)
                             .order_by(db.models.user_access.id)
                             .all())
            access = []
            active = None
            for field, acc in query_access:
                access.append(utils.row2dict(field))
                if acc.is_active:
                    active = acc.field

            users.append({
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'access': access,
                'active': active
            })
        return json.dumps(users)
    elif request.method == 'POST':
        # Create user
        # POST /api/user
        # {username:<username>, password:<password>, is_superuser:<is_superuser>}
        username = request.json.get('username')
        password = request.json.get('password', '')
        is_superuser = request.json.get('is_superuser')
        access = request.json.get('access', [])
        active = request.json.get('active')

        if not username:
            return 'No username', 404
        elif len(password) < 6:
            return 'Password length must be greater or equal to 6', 404
        elif not utils.validate_password_combination(password):
            return 'Password must contain at least three of them: Uppercase letters, ' \
                   'Lowercase letters, numbers and special symbols', 404

        # duplicate check
        user_record = g.session.query(db.models.user).filter(db.models.user.username == username).count()
        if user_record > 0:
            return 'The username "{}" already exists'.format(username), 404

        password = generate_password_hash(password)

        new_user = db.models.user(username=username,
                                  password=password,
                                  is_superuser=is_superuser)
        g.session.add(new_user)
        g.session.commit()

        for field in access:
            new_access = db.models.user_access(user=new_user.id, field=field.get('id'))
            if field.get('id') == active:
                new_access.is_active = True
            g.session.add(new_access)
        g.session.commit()

        return json.dumps(utils.row2dict(new_user))
    elif request.method == 'PUT':
        # Update user
        # PUT /api/user
        # {id:<id>, username:<username>, is_superuser:<is_superuser>}
        id_ = request.json.get('id')
        username = request.json.get('username')
        is_superuser = request.json.get('is_superuser')
        access = request.json.get('access', [])
        active = request.json.get('active')

        # duplicate check
        user_record = (g.session
                        .query(db.models.user)
                        .filter(db.models.user.username == username,
                                db.models.user.id != id_)
                        .count())
        if user_record > 0:
            return 'The username "{}" already exists'.format(username), 404

        (g.session
          .query(db.models.user)
          .filter(db.models.user.id == id_)
          .update({'username': username,
                   'is_superuser': is_superuser}))
        (g.session
          .query(db.models.user_access)
          .filter(db.models.user_access.user == id_)
          .delete())
        for field in access:
            new_access = db.models.user_access(user=id_, field=field.get('id'))
            if field.get('id') == active:
                new_access.is_active = True
            g.session.add(new_access)
        g.session.commit()

        return 'ok'
    elif request.method == 'DELETE':
        # Delete user
        # DELETE /api/user?id=<id>
        id_ = request.args.get('id')
        (g.session
          .query(db.models.user_access)
          .filter(db.models.user_access.user == id_)
          .delete())
        (g.session
          .query(db.models.user)
          .filter(db.models.user.id == id_)
          .delete())
        g.session.commit()

        return 'ok'

    abort(404)


@api.route('/sensor', methods=['GET', 'POST', 'PUT', 'DELETE'])
@utils.required_superuser
def api_sensor():
    if request.method == 'GET':
        # Read sensor
        # GET /api/sensor
        sensors = g.session.query(db.models.sensor).order_by(db.models.sensor.id).all()
        return json.dumps([utils.row2dict(sensor) for sensor in sensors])
    elif request.method == 'POST':
        # Create sensor
        # POST /api/sensor
        # {name:<string>, df_name:<string>, alias:<string>, unit:<string>,
        #  icon:<string>, bg_color:<string>}
        df_name = request.json.get('df_name')
        name = request.json.get('name')
        if not df_name:
            return 'No df_name', 404
        if not name:
            return 'No name', 404

        # duplicate check
        sensor_record = (g.session
                          .query(db.models.sensor)
                          .filter(or_(db.models.sensor.name == name,
                                      db.models.sensor.df_name == df_name))
                          .count())
        if sensor_record > 0:
            return 'The sensor name "{}" or df_name "{}" already exists'.format(name, df_name), 404

        db.inject_new_model(re.sub(r'-O[\d]*$', '', df_name))

        new_sensor = db.models.sensor(df_name=df_name,
                                      name=request.json.get('name'),
                                      alias=request.json.get('alias'),
                                      unit=request.json.get('unit'),
                                      icon=request.json.get('icon'),
                                      bg_color=request.json.get('bg_color'))
        g.session.add(new_sensor)
        g.session.commit()

        return json.dumps(utils.row2dict(new_sensor))
    elif request.method == 'PUT':
        # Update sensor
        # PUT /api/sensor
        # {id:<int>, name:<string>, df_name:<string>, alias:<string>,
        #  unit:<string>, icon:<string>, bg_color:<string>}
        id_ = request.json.get('id')
        df_name = request.json.get('df_name')
        name = request.json.get('name')

        if not df_name:
            return 'No df_name', 404
        if not name:
            return 'No name', 404

        # duplicate check
        sensor_record = (g.session
                          .query(db.models.sensor)
                          .filter(or_(db.models.sensor.name == name,
                                      db.models.sensor.df_name == df_name),
                                  db.models.sensor.id != id_)
                          .count())
        if sensor_record > 0:
            return 'The sensor name "{}" or df_name "{}" already exists'.format(name, df_name), 404

        db.inject_new_model(re.sub(r'-O[\d]*$', '', df_name))

        (g.session
          .query(db.models.sensor)
          .filter(db.models.sensor.id == id_)
          .update(request.json))
        g.session.commit()

        return 'ok'
    elif request.method == 'DELETE':
        # Delete sensor
        # DELETE /api/sensor?id=<id>
        id_ = request.args.get('id')
        (g.session
          .query(db.models.sensor)
          .filter(db.models.sensor.id == id_)
          .delete())
        g.session.commit()

        return 'ok'

    abort(404)


@api.route('/field', methods=['GET', 'POST', 'PUT', 'DELETE'])
@utils.required_superuser
def api_field():
    if request.method == 'GET':

        fields = []
        query_fields = (g.session
                         .query(db.models.field)
                         .order_by(db.models.field.id)
                         .all())

        for field in query_fields:
            temp_field = utils.row2dict(field)
            query_field_sensor = (g.session
                                   .query(db.models.sensor.name,
                                          db.models.field_sensor.sensor,
                                          db.models.field_sensor.df_name,
                                          db.models.field_sensor.alias,
                                          db.models.field_sensor.unit,
                                          db.models.field_sensor.icon,
                                          db.models.field_sensor.bg_color,
                                          db.models.field_sensor.alert_min,
                                          db.models.field_sensor.alert_max)
                                   .select_from(db.models.field_sensor)
                                   .join(db.models.sensor)
                                   .filter(db.models.field_sensor.field == field.id)
                                   .order_by(db.models.field_sensor.id)
                                   .all())
            temp_field['sensors'] = []
            for sensor in query_field_sensor:
                temp_sensor = {
                    'name': sensor.name,
                    'sensor': sensor.sensor,
                    'df_name': sensor.df_name,
                    'alias': sensor.alias,
                    'unit': sensor.unit,
                    'icon': sensor.icon,
                    'bg_color': sensor.bg_color,
                    'alert_min': sensor.alert_min,
                    'alert_max': sensor.alert_max,
                }
                temp_field['sensors'].append(temp_sensor)
            fields.append(temp_field)

        return json.dumps(fields)
    elif request.method == 'POST':
        # Create field
        # POST /api/field
        # {name:<string>, alias:<string>, sensors: [<sensor>, ...]}
        name = request.json.get('name')
        if not name:
            return 'No field name', 404

        # duplicate check
        field_record = g.session.query(db.models.field).filter(db.models.field.name == name).count()
        if field_record > 0:
            return 'The field name "{}" already exists'.format(name), 404

        new_field = db.models.field(name=request.json.get('name'),
                                    alias=request.json.get('alias'),
                                    iframe=request.json.get('iframe', ''))
        g.session.add(new_field)
        g.session.commit()

        for sensor in request.json.get('sensors', []):
            new_sensor = db.models.field_sensor(
                field=new_field.id,
                sensor=sensor.get('sensor'),
                df_name=sensor.get('df_name'),
                alias=sensor.get('alias'),
                unit=sensor.get('unit'),
                icon=sensor.get('icon'),
                bg_color=sensor.get('bg_color'),
                alert_min=sensor.get('alert_min'),
                alert_max=sensor.get('alert_max'))
            g.session.add(new_sensor)
            g.session.commit()

        return json.dumps(utils.row2dict(new_field))
    elif request.method == 'PUT':
        # Update field
        # PUT /api/field
        # {name:<string>, alias:<string>, sensors: [<sensor>, ...]}
        id_ = request.json.get('id')
        name = request.json.get('name')
        alias = request.json.get('alias')
        iframe = request.json.get('iframe', '')
        sensors = request.json.get('sensors', [])

        if not name:
            return 'No field name', 404

        # duplicate check
        field_record = (g.session
                         .query(db.models.field)
                         .filter(db.models.field.name == name,
                                 db.models.field.id != id_)
                         .count())
        if field_record > 0:
            return 'The field name "{}" already exists'.format(name), 404

        (g.session
          .query(db.models.field)
          .filter(db.models.field.id == id_)
          .update({'name': name,
                   'alias': alias,
                   'iframe': iframe}))
        (g.session
          .query(db.models.field_sensor)
          .filter(db.models.field_sensor.field == id_)
          .delete())
        for sensor in sensors:
            df_name = sensor.get('df_name')
            db.inject_new_model(df_name.replace('-O', ''))

            new_sensor = db.models.field_sensor(
                field=id_,
                sensor=sensor.get('sensor'),
                df_name=sensor.get('df_name'),
                alias=sensor.get('alias'),
                unit=sensor.get('unit'),
                icon=sensor.get('icon'),
                bg_color=sensor.get('bg_color'),
                alert_min=sensor.get('alert_min'),
                alert_max=sensor.get('alert_max'))
            new_sensor.field = id_
            new_sensor.id = None
            g.session.add(new_sensor)
            g.session.commit()
        g.session.commit()

        return 'ok'
    elif request.method == 'DELETE':
        # Delete field
        # DELETE /api/field?id=<id>
        id_ = request.args.get('id')

        for attr in db.models.__dict__.values():
            if inspect.isclass(attr) and hasattr(attr, 'timestamp'):
                (g.session
                  .query(attr)
                  .filter(attr.field == id_)
                  .delete())
        (g.session
          .query(db.models.field_sensor)
          .filter(db.models.field_sensor.field == id_)
          .delete())
        (g.session
          .query(db.models.user_access)
          .filter(db.models.user_access.field == id_)
          .delete())
        (g.session
          .query(db.models.field)
          .filter(db.models.field.id == id_)
          .delete())
        g.session.commit()

        return 'ok'

    abort(404)


# Z-Score 離群值檢測
@api.route('/outlier_detection', methods=['POST'])
@utils.required_login
def outlier_detection():
    try:
        # 接收前端傳來的資料
        timestamps = request.json['timestamps']
        values = request.json['values']
        zscore_threshold = request.json.get('zscoreThreshold', 3)  # 預設閾值為3
        
        # 將數據轉換為 DataFrame
        df = pd.DataFrame({'time': timestamps, 'value': values})
        df['time'] = pd.to_datetime(df['time'])  # 確保時間格式正確
        df.set_index('time', inplace=True)
        
        # 計算 Z-score
        mean = df['value'].mean()
        std_dev = df['value'].std()
        df['zscore'] = (df['value'] - mean) / std_dev
        
        # 根據 Z-score 閾值篩選離群值
        outlier_indices = df[df['zscore'].abs() > zscore_threshold].index.tolist()
        outlier_index_positions = [df.index.get_loc(index) for index in outlier_indices]
        
        # 返回離群值的索引
        return jsonify({
            'outlierIndices': outlier_index_positions
        })
    except Exception as e:
        log.error(f"Error in Z-score outlier detection: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
    
# STL 資料分解
@api.route('/stl_decomposition', methods=['POST'])
@utils.required_login
def stl_decomposition():
    try:
        # 接收前端傳送的時間序列資料
        x_data = request.json['x']  # 接收時間數據
        y_data = request.json['y']  # 接收對應的數值數據
        period = request.json.get('period', 7)  # 週期，預設12（根據資料的性質可調整）
        
        # 構建 DataFrame，並將 x_data 作為索引
        df = pd.DataFrame({'time': x_data, 'value': y_data})
        df['time'] = pd.to_datetime(df['time'])  # 將時間轉換為 datetime 格式
        df.set_index('time', inplace=True)  # 設置時間為索引
        
        if len(df.columns) != 1:
            return jsonify({"error": "Only one column of data is expected."}), 400
        
        # 對 value 進行 STL 分解
        stl = STL(df['value'], period=period)
        result = stl.fit()

        fig = psp.make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                                subplot_titles=["Observed", "Trend", "Seasonal", "Residual"])
        # 繪製觀察值
        fig.add_trace(go.Scatter(x=df['value'].index, y=result.observed, mode='lines', name='Observed'), row=1, col=1)
        # 繪製趨勢
        fig.add_trace(go.Scatter(x=df['value'].index, y=result.trend, mode='lines', name='Trend'), row=2, col=1) #line=dict(color='red')
        # 繪製季節性
        fig.add_trace(go.Scatter(x=df['value'].index, y=result.seasonal, mode='lines', name='Seasonal'), row=3, col=1) #, line=dict(color='green')
        # 繪製殘差
        fig.add_trace(go.Scatter(x=df['value'].index, y=result.resid, mode='lines', name='Residual'), row=4, col=1) #, line=dict(color='purple')
        # 更新整個圖表的佈局
        fig.update_layout(height=900, title="STL Decomposition Chart", showlegend=False)

        # 將圖表轉換為 JSON 格式，傳回前端
        graph_json = pio.to_json(fig)

        return jsonify({
            'trend': result.trend.tolist(),
            'seasonal': result.seasonal.tolist(),
            'resid': result.resid.tolist(),
            'graph': graph_json
        })
    except Exception as e:
        log.error(f"Error in STL decomposition: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 特徵關聯矩陣
@api.route('/correlation_matrix', methods=['POST'])
@utils.required_login
def correlation_matrix():
    try:
        # 從請求中提取 traces
        traces = request.json['traces']

        # 將 traces 數據轉換為多個 DataFrame
        dfs = []
        for trace in traces:
            if 'timestamps' in trace and 'values' in trace and 'field' in trace and 'sensor' in trace:
                column_name = f"{trace['field']}-{trace['sensor']}"
                df = pd.DataFrame({
                    'timestamps': pd.to_datetime(trace['timestamps']),
                    column_name: trace['values']
                }).set_index('timestamps')
                dfs.append(df)

        # 合併所有 DataFrame，按時間戳對齊
        df_all = pd.concat(dfs, axis=1)
        # 填充缺失值（可以選擇插值或直接用 NaN）
        df_all = df_all.interpolate(method='time')  # 時間插值

        # 計算相關係數矩陣
        correlation_matrix = df_all.corr()

        # 使用 Plotly 繪製特徵關聯矩陣
        fig = ff.create_annotated_heatmap(
            z=correlation_matrix.values,
            x=list(correlation_matrix.columns),
            y=list(correlation_matrix.index),
            annotation_text=correlation_matrix.round(2).values,
            colorscale='Blues',
            showscale=True
        )

        # 返回整個圖表的 JSON 格式
        return jsonify({'fig': pio.to_json(fig)})

    except Exception as e:
        # 錯誤處理
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 400


@api.route('/plotly', methods=['POST'])
@utils.required_login
def plotly_api():
    try:
        # 從前端的請求中獲取資料，分別為 traces 跟 plot_method
        traces = request.json['traces']
        plot_method = request.json.get('plotmethod', 'line')


        all_traces = []
        for trace_data in traces: # 分別對每筆資料集進行繪圖，並存入 all_traces
            x = timestamps = trace_data['timestamps']
            y = values = trace_data['values']
            field = trace_data.get('field')
            sensor = trace_data.get('sensor')
            name = f"{field} - {sensor}" # DashBoard會截取field跟sensor，其他系統不需要，因此可以將name設定成自己的變數名稱

            trace, layout = create_trace(plot_method, x, y, name) # 創建單個 trace，並依序加入到 all_traces
            all_traces.append(trace)
        
        # 使用 to_plotly_json() 轉換 traces 和 layout ，這樣前端才能應用
        serialized_traces = [trace.to_plotly_json() for trace in all_traces]
        print(serialized_traces)

        # 將 traces 和 layout 分別返回
        return jsonify({'traces': serialized_traces, 'layout': layout}), 200

    except Exception as e:
        # 錯誤訊息以幫助診斷問題
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 400

# 生成繪圖資料trace的函式
def create_trace(plot_method, x, y, name): # DashBoard通常為時間序列資料，因此這裡的x = timestamps, y = values
    trace = go.Scatter(x=x, y=y, name=name, mode='lines+markers' if plot_method == 'line' else 'markers') # 預設trace
    layout = {
      'xaxis': {'title': 'Time', 'tickformat': '%Y-%m-%d %H:%M:%S', 'tickangle': 45},
      'yaxis': {'title': 'Value'}
    } # 預設layout

    if plot_method == 'heatmap':
        z_values = np.array(y).reshape(1, len(y)).tolist()
        trace = go.Heatmap(
            x=x,
            y=[name],
            z=z_values,
            colorscale='Viridis',
            showscale=True
        )
    elif plot_method == 'box':
      trace = go.Box(y=y, name=name)
    elif plot_method == 'bar':
      trace = go.Bar(x=x, y=y, name=name)
    elif plot_method == 'histogram':
      trace = go.Histogram(x=y, name=name)
      layout = {'xaxis': {}, 'yaxis': {}}
    elif plot_method == 'area':
      trace = go.Scatter(x=x, y=y, name=name, mode='lines', fill='tozeroy')    

    return trace, layout
    
