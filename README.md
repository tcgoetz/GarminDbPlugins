# GarminDbPlugins

## Building Your Own Plugin

### FIT Activity Files

Find out what fields your FIT file uses:
- Put a copy of your file in GarminDB/test/test_files/fit/activity
- in GarminDB/test run make test_fit_file.TestFitFile.test_parse_activity
- Look at test_filt_file.log for the parsed output of your FIT file.

Creating your FIT Activity file plugin.
- Copy Plugins\hrv_plugin.py and rename it for your activity type.
- Edit the dev fields list to match your file type.
- Change the table name in the table defines to match your file type.
- Change the table fields to match your dev fields.
- Change the view to match your fields.

After testing your plugin, submit a pull request on this repositoy against the develop branch.
