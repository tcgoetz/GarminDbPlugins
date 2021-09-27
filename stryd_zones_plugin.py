"""Plugin for processing for the IQ datafield Stryd Zones https://apps.garmin.com/en-US/apps/18fb2cf0-1a4b-430d-ad66-988c847421f4"""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging
import datetime
from sqlalchemy import Integer, Float, DateTime, String, ForeignKey, Time

from garmindb import ActivityFitPluginBase


logger = logging.getLogger(__file__)


def ms_to_dt_time(time_ms):
    """Convert time in milli seconds to a datetime object."""
    if time_ms is not None:
        return (datetime.datetime.min + datetime.timedelta(milliseconds=time_ms)).time()


# @classmethod
# def create_activity_view(cls, act_db):
#     """Create a database view for the Stryd Zones plugin data."""
#     view_selectable = [
#         cls.activity_id.label('activity_id'),
#         cls.activities_table.name.label('name'),
#         cls.activities_table.description.label('description'),
#         cls.activities_table.sub_sport.label('sub_sport'),
#         cls.activities_table.start_time.label('start_time'),
#         cls.activities_table.stop_time.label('stop_time'),
#         cls.activities_table.elapsed_time.label('elapsed_time'),
#         cls.activities_table.avg_hr.label('avg_hr'),
#         cls.activities_table.max_hr.label('max_hr'),
#         cls.activities_table.avg_rr.label('avg_rr'),
#         cls.activities_table.max_rr.label('max_rr'),
#         cls.round_ext_col(cls.activities_table, 'calories'),
#         cls.round_ext_col(cls.activities_table, 'avg_temperature'),
#         cls.activities_table.avg_cadence.label('avg_rpms'),
#         cls.activities_table.max_cadence.label('max_rpms'),
#         cls.round_ext_col(cls.activities_table, 'avg_speed'),
#         cls.round_ext_col(cls.activities_table, 'max_speed'),
#         cls.stance_time.label('stance_time'),
#         cls.round_col('avg_vertical_oscillation'),
#         cls.round_col('power'),
#         cls.activities_table.training_effect.label('training_effect'),
#         cls.activities_table.anaerobic_training_effect.label('anaerobic_training_effect')
#     ]
#     view_name = 'stryd_zones_activities'
#     logger.info("Creating view %s of %s and %s if needed.", view_name, cls, cls.activities_table)
#     cls.create_join_view(act_db, view_name, view_selectable, cls.activities_table, order_by=cls.activities_table.start_time.desc())


class stryd_zones(ActivityFitPluginBase):
    """Plugin for processing for the IQ data field stryd zones."""

    _application_id = bytearray(b'\x18\xfb,\xf0\x1aKC\r\xadf\x98\x8c\x84t!\xf4')

    _records_tablename = 'stryd_zones_records'
    _records_version = 1
    _records_pk = ("activity_id", "record")
    _records_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')]},
        'record': {'args': [Integer]},
        'timestamp': {'args': [DateTime]},
        'power': {'args': [Float], 'units': 'Watts'},
        'cadence': {'args': [Integer], 'units': 'rpm'},
        'stance_time': {'args': [Time], 'units': 'Milliseconds'},
        'avg_vertical_oscillation': {'args': [Integer], 'units': 'Centimeters'},
        'elevation': {'args': [Float], 'units': 'Meters'},
        'form_power': {'args': [Float], 'units': 'Watts'},
        'leg_spring_stiffness': {'args': [Float], 'units': 'kN/m'}
    }

    _tables = {}
    # _views = {'activity_view': create_activity_view}

    def write_record_entry(self, activity_db_session, fit_file, activity_id, message_fields, record_num):
        """Write a record message into the plugin records table."""
        record = {
            'cadence': message_fields.get('dev_cadence')
        }
        record_table = self._tables['record']
        if not record_table.s_exists(activity_db_session, {'activity_id' : activity_id, 'record' : record_num}):
            plugin_record = {
                'activity_id'                   : activity_id,
                'record'                        : record_num,
                'timestamp'                     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                # 'power'                         : message_fields.get('dev_Power'),
                'stance_time'                   : ms_to_dt_time(message_fields.get('dev_stance_time')),
                'avg_vertical_oscillation'      : message_fields.get('dev_avg_vertical_oscillation'),
                'elevation'                     : message_fields.get('dev_Elevation'),
                'form_power'                    : message_fields.get('dev_Form Power'),
                'leg_spring_stiffness'          : message_fields.get('dev_Leg Spring Stiffness')
            }
            plugin_record.update(record)
            logger.info("writing %s record %r for %s", self.__class__.__name__, plugin_record, fit_file.filename)
            activity_db_session.add(record_table(**plugin_record))
        return record
