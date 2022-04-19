# GarminDbPlugins

## Installing Plugins

Download the plugin source from this repo and copy it to ~/HealthData/Plugin.

## Building Your Own Plugin

### FIT Activity Files

Find out what fields your FIT file uses:
- Put a copy of a FIT file that contains the data you are writing the plugin for in GarminDB/test/test_files/fit/activity
- In GarminDB/test run `make test_fit_file.TestFitFile.test_parse_activity`
- Look at fit_file.log for the parsed output of your FIT file.
- Some of the ineteresting message types to look at the `MessageType.sport` (sport and sub sport fields), `MessageType.dev_data_id` (developer app or datafield ids), `essageType.field_description` (developer defined fields), `MessageType.record` (data recorded at regular intervals throughout the activity), `MessageType.lap` (per lap data), and `MessageType.session` (summary data, generally one session per activity).

Creating your FIT Activity file plugin:
- Copy Plugins/hrv_plugin.py and rename it for your activity type.
- Decide how the plugin will be matched to FIT files:
  - Match on the app id of a Connect IQ app or data field.You can find the app id from the parse output of the FIT file by searching for `MessageType.dev_data_id` and finding the `application_id` field.
  - To match via dev fields, add a _dev_fields class member to contains a list of the dev fields to match to.
  - You can also match on sport and sub sport with the `_sport` and `_sub_sport` class members.
- Decide what kind of data you are saving.
  - The most commonly used message types in activity files are records, laps, and sessions. Decide which of those you will be saving data from.
  - Define tables for records, laps, and sessions depending upon your needs. Examples can be found in existing plugins.
    - Change the table names to match your plugin.
    - Change to table field names and types to suite your data. 
- Decide if your data needs a database view and change your plugins create_activity_view function to match your fields.

Test your plugin:
- Publish a copy of your plugin to the ~/HealthData/Plugins directory.
- Put a copy of your FIT file in GarminDB/test/test_files/fit/activity
- in GarminDB/test run `make test_activities_db.TestActivitiesDb.test_fit_file_import`
- The test creates a activities.db in a temp directory which is listed in the output.
- Load the DB and check the tables, fields, and views.

After testing your plugin, submit a pull request on this repository against the develop branch. After the pull request has been review it will be merged to the master branch.
