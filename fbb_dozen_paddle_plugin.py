"""Plugin for processing for the IQ data field Dozen Paddle from fbbbrown."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging
from sqlalchemy import Integer, Float, DateTime, String, ForeignKey

from activity_plugin_base import ActivityPluginBase


logger = logging.getLogger(__file__)


class fbb_dozen_paddle(ActivityPluginBase):
    """Plugin for processing for the IQ data field Dozen Paddle from fbbbrown."""

    _application_id = bytearray(b'\xd6x,\x853\xf6D{\xb3Rza\xfa\x90SS')

    _records_tablename = 'dozen_paddle_records'
    _records_version = 1
    _records_pk = ("activity_id", "record")
    _records_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')]},
        'record': {'args': [Integer]},
        'timestamp': {'args': [DateTime]},
        'stroke_distance': {'args': [Float]}
    }

    _tables = {}
    _views = {}

    def write_record_entry(self, activity_db_session, fit_file, activity_id, message_fields, record_num):
        """Write a record message into the plugin records table."""
        record_table = self._tables['record']
        if not record_table.s_exists(activity_db_session, {'activity_id' : activity_id, 'record' : record_num}):
            record = {
                'activity_id'       : activity_id,
                'record'            : record_num,
                'timestamp'         : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'stroke_distance'   : message_fields.get('dev_sd')
            }
            logger.debug("writing %s record %r for %s", self.__class__.__name__, record, fit_file.filename)
            activity_db_session.add(record_table(**record))
        return {}

    def write_paddle_entry(self, activity_db_session, fit_file, activity_id, sub_sport, message_fields):
        """Write a session message into the plugin's sessions table."""
        stroke_count = message_fields.get('dev_sc')
        return {'strokes': stroke_count} if stroke_count else {}
