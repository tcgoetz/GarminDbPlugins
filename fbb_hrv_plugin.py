"""Plugin for processing heart rate variance data from the IQ application Heart Monitor + HRV from fbbbrown: https://apps.garmin.com/en-US/apps/ff2e268f-bdcc-4580-b03e-809336d56f2a."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging
from sqlalchemy import Integer, DateTime, String, ForeignKey

from garmindb import ActivityFitPluginBase


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
        cls.min_hr.label('min_hr'),
        cls.hrv_rmssd.label('hrv_rmssd'),
        cls.hrv_sdrr_f.label('hrv_sdrr_f'),
        cls.hrv_sdrr_l.label('hrv_sdrr_l'),
        cls.hrv_pnn50.label('hrv_pnn50'),
        cls.hrv_pnn20.label('hrv_pnn20')
    ]
    view_name = 'hrv_activities_view'
    logger.info("Creating hrv plugin view %s if needed.", view_name)
    cls.create_join_view(act_db, view_name, view_selectable, cls.activities_table, order_by=cls.activities_table.start_time.desc())


class fbb_hrv(ActivityFitPluginBase):
    """A GarminDb plugin for saving data from the IQ application Heart Monitor + HRV from fbbbrown."""

    _application_id = bytearray(b'\x0b\xdc\x0eu\x9b\xaaAz\x8c\x9f\xe9vf*].')

    _records_tablename = 'hrv_records'
    _records_version = 1
    _records_pk = ("activity_id", "record")
    _records_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')]},
        'record': {'args': [Integer]},
        'timestamp': {'args': [DateTime]},
        'hrv_s': {'args': [Integer], 'units': 'ms'},
        'hrv_btb': {'args': [Integer], 'units': 'ms'},
        'hrv_hr': {'args': [Integer], 'unis': 'bpm'}
    }

    _sessions_tablename = 'hrv_sessions'
    _sessions_version = 1
    _sessions_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')], 'kwargs': {'primary_key': True}},
        'timestamp': {'args': [DateTime]},
        'min_hr': {'args': [Integer], 'units': 'bpm'},
        'hrv_rmssd': {'args': [Integer], 'units': 'bpm'},
        'hrv_sdrr_f': {'args': [Integer], 'units': 'bpm'},
        'hrv_sdrr_l': {'args': [Integer], 'units': 'bpm'},
        'hrv_pnn50': {'args': [Integer], 'units': '%'},
        'hrv_pnn20': {'args': [Integer], 'units': '%'}
    }

    _tables = {}
    _views = {'activity_view': create_activity_view}

    def write_record_entry(self, activity_db_session, fit_file, activity_id, message_fields, record_num):
        """Write a record message into the plugin records table."""
        record_table = self._tables['record']
        if not record_table.s_exists(activity_db_session, {'activity_id' : activity_id, 'record' : record_num}):
            record = {
                'activity_id'   : activity_id,
                'record'        : record_num,
                'timestamp'     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'hrv_s'         : message_fields.get('dev_hrv_s'),
                'hrv_btb'       : message_fields.get('dev_hrv_btb'),
                'hrv_hr'        : message_fields.get('dev_hrv_hr'),
            }
            logger.debug("writing hrv record %r for %s", record, fit_file.filename)
            activity_db_session.add(record_table(**record))
        return {}

    def write_session_entry(self, activity_db_session, fit_file, activity_id, message_fields):
        """Write a session message into the plugin sessions table."""
        session_table = self._tables['session']
        if not session_table.s_exists(activity_db_session, {'activity_id' : activity_id}):
            session = {
                'activity_id'   : activity_id,
                'timestamp'     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'min_hr'        : message_fields.get('dev_min_hr'),
                'hrv_rmssd'     : message_fields.get('dev_hrv_rmssd'),
                'hrv_sdrr_f'    : message_fields.get('dev_hrv_sdrr_f'),
                'hrv_sdrr_l'    : message_fields.get('dev_hrv_sdrr_l'),
                'hrv_pnn50'     : message_fields.get('dev_hrv_pnn50'),
                'hrv_pnn20'     : message_fields.get('dev_hrv_pnn20'),
            }
            logger.debug("writing hrv session %r for %s", session, fit_file.filename)
            activity_db_session.add(session_table(**session))
        return {}
