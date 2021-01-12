"""Plugin for processing for the IQ data field Dozen Paddle from fbbbrown."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging

from activity_plugin_base import ActivityPluginBase


logger = logging.getLogger(__file__)


class fbb_dozen_paddle(ActivityPluginBase):
    """Plugin for processing for the IQ data field Dozen Paddle from fbbbrown."""

    _application_id = bytearray(b'\xd6x,\x853\xf6D{\xb3Rza\xfa\x90SS')

    #
    # This app has a lot of fields in its dev fields description but only a few are populated. If you have examples where more of the fields are populated than are
    # represented here, please send in the example FIT file and I will add the additional fields.
    #

    _tables = {}
    _views = {}

    def write_paddle_entry(self, activity_db_session, fit_file, activity_id, sub_sport, message_fields):
        """Write a session message into the plugin's sessions table."""
        stroke_count = message_fields.get('dev_sc')
        return {'strokes': stroke_count} if stroke_count else {}
