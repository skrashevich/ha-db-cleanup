# Homeassistant DB Cleanup and Recovery

*WARNING*: Limited testing has been done so use at own risk!

Quick and dirty tool to cleanup entities and devices inside Home Assistant that you cannot otherwise remove.  This helps in situations where you do not want to blow away the integration to remove duplicates/dead items.

## Usage
1. Clone the repo
2. Downlaod copies of your `core.device_registry` and `core.entity_registry` to the folder of cloned repo
3. Run `./main.py`


## Notes
* Tested on python 2.7, and 3.9 via OSX without issue.  Testing/PR's for Windows welcome
* It is not perfect.  Feel free to PR fixes.
* No modifications to the files are done unless you run the cleanup aspect.  It is recommended to do the work on your local machine versus directly on HA server.

