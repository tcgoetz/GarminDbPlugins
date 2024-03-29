"""Plugin for processing for the IQ data field Dozen Walk from fbbbrown: https://apps.garmin.com/en-US/apps/e2ad0aa2-335d-4122-888d-ce4305ca5a9a."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"

import logging

from garmindb import ActivityFitPluginBase


logger = logging.getLogger(__file__)


class fbb_dozen_walk(ActivityFitPluginBase):
    """Plugin for processing for the IQ data field Dozen Walk from fbbbrown."""

    _application_id = bytearray(b'\xe2\xad\n\xa23]A"\x88\x8d\xceC\x05\xcaZ\x9a')

    _tables = {}
    _views = {}

    def write_steps_entry(self, activity_db_session, fit_file, activity_id, sub_sport, message_fields):
        """Return a steps reading to be included in the steps activities table."""
        steps = message_fields.get('dev_S')
        return {'steps': steps} if steps else {}
