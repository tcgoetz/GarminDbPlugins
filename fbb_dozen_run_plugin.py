"""Plugin for processing for the IQ data field Dozen Run from fbbbrown."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging
from sqlalchemy import Integer, Float, DateTime, String, ForeignKey

from activity_plugin_base import ActivityPluginBase


logger = logging.getLogger(__file__)


@classmethod
def create_activity_view(cls, act_db):
    """Create a database view for the Dozen Cycle plugin data."""
    view_selectable = [
        cls.activity_id.label('activity_id'),
        cls.activities_table.name.label('name'),
        cls.activities_table.description.label('description'),
        cls.activities_table.sub_sport.label('sub_sport'),
        cls.activities_table.start_time.label('start_time'),
        cls.activities_table.stop_time.label('stop_time'),
        cls.activities_table.elapsed_time.label('elapsed_time'),
        cls.activities_table.avg_hr.label('avg_hr'),
        cls.activities_table.max_hr.label('max_hr'),
        cls.activities_table.avg_rr.label('avg_rr'),
        cls.activities_table.max_rr.label('max_rr'),
        cls.round_ext_col(cls.activities_table, 'calories'),
        cls.round_ext_col(cls.activities_table, 'avg_temperature'),
        cls.activities_table.avg_cadence.label('avg_rpms'),
        cls.activities_table.max_cadence.label('max_rpms'),
        cls.round_ext_col(cls.activities_table, 'avg_speed'),
        cls.round_ext_col(cls.activities_table, 'max_speed'),
        cls.round_col('estimated_power_avg'),
        cls.round_col('max_power'),
        cls.round_col('max_ftp'),
        cls.round_col('normalized_power'),
        cls.activities_table.training_effect.label('training_effect'),
        cls.activities_table.anaerobic_training_effect.label('anaerobic_training_effect')
    ]
    view_name = 'dozen_run_activities'
    logger.info("Creating view %s of %s and %s if needed.", view_name, cls, cls.activities_table)
    cls.create_join_view(act_db, view_name, view_selectable, cls.activities_table, order_by=cls.activities_table.start_time.desc())


class fbb_dozen_run(ActivityPluginBase):
    """Plugin for processing for the IQ data field Dozen Run from fbbbrown."""

    _application_id = bytearray(b'\x9f\xf7Z\xfa\xd5\x94C\x11\x89\xf7\xf9,\xa0!\x18\xad')

    _records_tablename = 'dozen_run_records'
    _records_version = 1
    _records_pk = ("activity_id", "record")
    _records_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')]},
        'record': {'args': [Integer]},
        'timestamp': {'args': [DateTime]},
        'momentary_energy_expenditure': {'args': [Float]},
        'relative_running_economy': {'args': [Float]},
        'power': {'args': [Float]},
        'training_peaks_re': {'args': [Float]},
        'fellnr_re': {'args': [Float]}
    }

    _sessions_tablename = 'dozen_run_sessions'
    _sessions_version = 1
    _sessions_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')], 'kwargs': {'primary_key': True}},
        'timestamp': {'args': [DateTime]},
        'avg_running_economy': {'args': [Float]},
        'avg_power': {'args': [Float]},
        'avg_training_peaks_re': {'args': [Float]},
        'xuxumatu_re': {'args': [Float]}
    }

    _tables = {}
    _views = {'activity_view': create_activity_view}

    def write_record_entry(self, activity_db_session, fit_file, activity_id, message_fields, record_num):
        """Write a record message into the plugin records table."""
        record_table = self._tables['record']
        if not record_table.s_exists(activity_db_session, {'activity_id' : activity_id, 'record' : record_num}):
            record = {
                'activity_id'                   : activity_id,
                'record'                        : record_num,
                'timestamp'                     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'momentary_energy_expenditure'  : message_fields.get('dev_eE'),
                'relative_running_economy'      : message_fields.get('dev_rE'),
                'power'                         : message_fields.get('dev_pwr'),
                'training_peaks_re'             : message_fields.get('dev_tpRE'),
                'fellnr_re'                     : message_fields.get('frnrRE'),
            }
            logger.info("writing %s record %r for %s", self.__class__.__name__, record, fit_file.filename)
            activity_db_session.add(record_table(**record))
        return {}

    def write_steps_entry(self, activity_db_session, fit_file, activity_id, sub_sport, message_fields):
        """Write a session message into the plugin's sessions table."""
        session_table = self._tables['session']
        steps = message_fields.get('dev_tS')
        if not session_table.s_exists(activity_db_session, {'activity_id' : activity_id}):
            session = {
                'activity_id'           : activity_id,
                'timestamp'             : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'avg_running_economy'   : message_fields.get('dev_aE'),
                'avg_power'             : message_fields.get('dev_apwr'),
                'avg_training_peaks_re' : message_fields.get('dev_tpaRE'),
                'xuxumatu_re'           : message_fields.get('dev_xRE'),
            }
            logger.info("writing %s session %r for %s message %r", self.__class__.__name__, session, fit_file.filename, message_fields)
            activity_db_session.add(session_table(**session))
        return {'steps': steps} if steps else {}
