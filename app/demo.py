import logging

from datetime import datetime
from dateutil import parser

from flask import (Blueprint, abort, jsonify, g,
                   render_template as flast_render_template, request)

import config

from . import utils
from db import db

log = logging.getLogger("\033[1;34m[DEMO]\033[0m")
demo_api = Blueprint('DEMO', __name__)


def render_demo_template(*args, **argv):
    target_field = argv.get('field')
    if not target_field:
        abort(404)

    field_record = (g.session
                     .query(db.models.field)
                     .filter(db.models.field.name == target_field)
                     .first())
    if not field_record:
        abort(404)

    sensors = []
    sensor_records = (g.session
                       .query(db.models.field_sensor)
                       .filter(db.models.field_sensor.field == field_record.id)
                       .order_by(db.models.field_sensor.id)
                       .all())
    for sensor in sensor_records:
        sensors.append(utils.row2dict(sensor))

    return flast_render_template(*args,
                                 fieldname=target_field,
                                 sensors=sensors,
                                 timeout_strikethrough=config.TIMEOUT_STRIKETHROUGH,
                                 **argv)


@demo_api.route('/<string:field>', methods=['GET'])
def demo(field):
    token = request.args.get('token')
    if token != config.demo_token.get(field):
        abort(404)
    return render_demo_template('demo.html', field=field, token=token)


@demo_api.route('/h/<string:field>', methods=['GET'])
def demo_history(field):
    token = request.args.get('token')
    if token != config.demo_token.get(field):
        abort(404)
    return render_demo_template('demo_history.html', field=field, token=token)


@demo_api.route('/datas/<string:field>', methods=['GET'])
def api_query_demo_data(field):
    token = request.args.get('token')
    if token != config.demo_token.get(field):
        abort(404)

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

        res.update({df_name: [(str(r.timestamp), r.value) for r in query]})

    etime = datetime.now()
    log.debug((etime - stime).total_seconds())
    return jsonify(res)


@demo_api.route('/datas/<string:field>/<string:df_name>', methods=['GET'])
def api_query_demo_history_data(field, df_name):
    token = request.args.get('token')
    if token != config.demo_token.get(field):
        abort(404)

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

    res = {df_name: [(str(r.timestamp), r.value) for r in query]}

    etime = datetime.now()
    log.debug((etime - stime).total_seconds())
    return jsonify(res)
