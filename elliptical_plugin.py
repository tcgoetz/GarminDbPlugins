"""Plugin for processing heart rate variance data from the IQ application Elliptical from fbbbrown."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging
from sqlalchemy import Integer, Float, DateTime, String, ForeignKey

from activity_plugin_base import ActivityPluginBase


logger = logging.getLogger(__file__)


@classmethod
def create_activity_view(cls, act_db):
    """Create a database view for the hrv plugin data."""
    view_selectable = [
        cls.activities_table.activity_id.label('activity_id'),
        cls.activities_table.name.label('name'),
        cls.activities_table.description.label('description'),
        cls.activities_table.start_time.label('start_time'),
        cls.activities_table.stop_time.label('stop_time'),
        cls.activities_table.elapsed_time.label('elapsed_time'),
        cls.steps.label('steps'),
        cls.distance.label('distance'),
        cls.activities_table.avg_hr.label('avg_hr'),
        cls.activities_table.max_hr.label('max_hr'),
        cls.activities_table.avg_rr.label('avg_rr'),
        cls.activities_table.max_rr.label('max_rr'),
        cls.round_ext_col(cls.activities_table, 'calories'),
        cls.avg_cadence.label('avg_cadence'),
        cls.activities_table.training_effect.label('training_effect'),
        cls.activities_table.anaerobic_training_effect.label('anaerobic_training_effect')
    ]
    view_name = 'elliptical_activities'
    logger.info("Creating elliptical view %s if needed.", view_name)
    cls.create_join_view(act_db, view_name, view_selectable, cls.activities_table, order_by=cls.activities_table.start_time.desc())


class elliptical(ActivityPluginBase):
    """A GarminDb plugin for saving data from the IQ application Elliptical from fbbbrown."""

    _application_id = bytearray(b'\x17+\xdc\xa5&\x8eL\x0e\xbbn\x12\xbe\xeej\xdc\x17')

    _sport = 4  # Sport.fitness_equipment: 4
    _sub_sport = 15  # SubSport.elliptical: 15

    _records_tablename = 'elliptical_records'
    _records_version = 1
    _records_pk = ("activity_id", "record")
    _records_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')]},
        'record': {'args': [Integer]},
        'timestamp': {'args': [DateTime]},
        'distance': {'args': [Integer]},
        'speed': {'args': [Integer]},
        'cadence': {'args': [Integer]}
    }

    _sessions_tablename = 'elliptical_sessions'
    _sessions_version = 1
    _sessions_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')], 'kwargs': {'primary_key': True}},
        'timestamp': {'args': [DateTime]},
        'distance': {'args': [Integer]},
        'steps': {'args': [Integer]},
        'avg_cadence': {'args': [Integer]},
        'battery_used': {'args': [Float]}
    }

    _tables = {}
    _views = {'activity_view': create_activity_view}

    def write_record_entry(self, activity_db_session, fit_file, activity_id, message_fields, record_num):
        """Write a record message into the plugin records table."""
        record = {
            'distance'      : message_fields.get('dev_distance'),
            'speed'         : message_fields.get('dev_speed'),
            'cadence'       : message_fields.get('dev_cadence')
        }
        record_table = self._tables['record']
        if not record_table.s_exists(activity_db_session, {'activity_id' : activity_id, 'record' : record_num}):
            plugin_record = {
                'activity_id'   : activity_id,
                'record'        : record_num,
                'timestamp'     : fit_file.utc_datetime_to_local(message_fields.timestamp)
            }
            plugin_record.update(record)
            logger.debug("writing %s record %r for %s", self.__class__.__name__, plugin_record, fit_file.filename)
            activity_db_session.add(record_table(**plugin_record))
        return record

    def write_session_entry(self, activity_db_session, fit_file, activity_id, message_fields):
        """Write a session message into the plugin sessions table."""
        # some field names veried with versions of the app, so we check for all possible field names
        distance = self._get_field(message_fields, ['dev_total_distance', 'dev_distance'])
        avg_cadence = message_fields.get('dev_avg_cadence')
        session_table = self._tables['session']
        if not session_table.s_exists(activity_db_session, {'activity_id' : activity_id}):
            session = {
                'activity_id'   : activity_id,
                'timestamp'     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'distance'      : distance,
                'avg_cadence'   : avg_cadence,
                'steps'         : self._get_field(message_fields, ['dev_tStps', 'dev_Stps', 'dev_Steps', 'dev_ts', 'total_steps']),
                'battery_used'  : self._get_field(message_fields, ['dev_%bat', 'BatteryUsed'])
            }
            logger.info("writing %s session %r for %s message %r", self.__class__.__name__, session, fit_file.filename, message_fields)
            activity_db_session.add(session_table(**session))
        return {
            'distance'      : distance,
            'avg_cadence'   : avg_cadence,
            'calories'      : message_fields.get('dev_tcal'),
        }
