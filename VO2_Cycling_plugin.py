"""Plugin for processing for the IQ data field JMG-DTF Cycling VO2 Max: https://apps.garmin.com/en-US/apps/d7ec9b1b-8353-42e9-a3d3-c8ac641a2dba"""


__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging
from sqlalchemy import Integer, Float, DateTime, String, ForeignKey

from garmindb import ActivityFitPluginBase


logger = logging.getLogger(__file__)
@classmethod

def create_activity_view(cls, act_db):
    """Create a database view for the VO2 Cycling plugin data."""
    view_selectable = [
        cls.activity_id.label('activity_id'),
        cls.activities_table.name.label('name'),
        cls.activities_table.description.label('description'),
        cls.activities_table.sub_sport.label('sub_sport'),
        cls.activities_table.start_time.label('start_time'),
        cls.activities_table.stop_time.label('stop_time'),
        cls.activities_table.elapsed_time.label('elapsed_time'),
        cls.activities_table.avg_hr.label('avg_hr'),
        cls.activities_table.avg_rr.label('avg_rr'),
        cls.round_ext_col(cls.activities_table, 'calories'),
        cls.round_ext_col(cls.activities_table, 'avg_temperature'),
        cls.activities_table.avg_cadence.label('avg_rpms'),
        cls.round_ext_col(cls.activities_table, 'avg_speed'),
        cls.VO2maxSession.label('VO2maxSession'),
        cls.VO2maxSmooth.label('VO2maxSmooth'),
    ]
    view_name = 'VO2_cycle_activities'
    logger.info("Creating view %s of %s and %s if needed.", view_name, cls, cls.activities_table)
    cls.create_join_view(act_db, view_name, view_selectable, cls.activities_table, order_by=cls.activities_table.start_time.desc())



class VO2_Cycling(ActivityFitPluginBase):
    """A GarminDb plugin for saving data from the IQ application VO2 Cyclying."""
    _application_id = bytearray(b'\xd7\xec\x9b\x1b\x83SB\xe9\xa3\xd3\xc8\xacd\x1a-\xba')
    _sport = "cycling"
    
    _records_pk = ("activity_id", "record")
    _records_tablename = 'VO2_Cycling_Records'
    _records_version = 1
    _records_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')]},
        'record': {'args': [Integer]},
        'timestamp': {'args': [DateTime]},
        'VO2': {'args': [Float], 'units': 'ml/min/kg'}
    }
    
    _sessions_tablename = 'VO2_Cycling_Session'
    _sessions_version = 1
    _sessions_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')], 'kwargs': {'primary_key': True}},
        'timestamp': {'args':    [DateTime]},
        'VO2maxSession':{'args': [Float],'units':'ml/min/kg'},
        'VO2maxSmooth': {'args': [Float],'units':'ml/min/kg'}
    }
    _tables = {}
    _views = {'activity_view': create_activity_view}
    
    def write_record_entry(self, activity_db_session, fit_file, activity_id, message_fields, record_num):
        """Write a record message into the plugin records table."""
        record_table = self._tables['record']
        if not record_table.s_exists(activity_db_session, {'activity_id' : activity_id, 'record' : record_num}):
            record = {
                'activity_id'       : activity_id,
                'record'            : record_num,
                'timestamp'         : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'VO2'               : message_fields.get('dev_VO2'),
            }
            logger.debug("writing %s record %r for %s", self.__class__.__name__, record, fit_file.filename)
            activity_db_session.add(record_table(**record))
        return {}

    def write_session_entry(self, activity_db_session, fit_file, activity_id, message_fields):
        """Write a session message into the plugin sessions table."""
        session_table = self._tables['session']
        if not session_table.s_exists(activity_db_session, {'activity_id' : activity_id}):
            
            VO2maxSmooth = message_fields.get('dev_VO2maxSmooth') 
            if VO2maxSmooth == None:
                VO2maxSmooth = message_fields.get('dev_VO2mean')
            
            session = {
                'activity_id'   : activity_id,
                'timestamp'     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'VO2maxSession' : message_fields.get('dev_VO2maxSession'),
                'VO2maxSmooth'  : VO2maxSmooth,
            }

            logger.debug("writing VO2 session %r for %s", session, fit_file.filename)
            activity_db_session.add(session_table(**session))
        return {}