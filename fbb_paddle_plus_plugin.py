"""Plugin for processing for the IQ App Paddle Plus from fbbbrown: https://apps.garmin.com/en-US/apps/749a7702-3ec5-42be-b9e3-731b1b13f7f6."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging

from garmindb import ActivityPluginBase


logger = logging.getLogger(__file__)


class fbb_paddle_plus(ActivityPluginBase):
    """Plugin for processing for the IQ data field Dozen Paddle from fbbbrown."""

    _application_id = bytearray(b't\x9aw\x02>\xc5B\xbe\xb9\xe3s\x1b\x1b\x13\xf7\xf6')

    _tables = {}
    _views = {}

    def write_paddle_entry(self, activity_db_session, fit_file, activity_id, sub_sport, message_fields):
        """Write a session message into the plugin's sessions table."""
        paddle = {
            'strokes'               : message_fields.get('dev_tStrk'),
            'avg_stroke_distance'   : message_fields.get('dev_aSrd')
        }
        return self.filter_data(paddle)

    def write_session_entry(self, activity_db_session, fit_file, activity_id, message_fields):
        """Write a session message into the plugin sessions table."""
        session = {
            'distance'      : message_fields.get('dev_Tdst'),
            'calories'      : message_fields.get('dev_Tcal'),
        }
        return self.filter_data(session)
