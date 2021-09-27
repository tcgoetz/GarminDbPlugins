

PLUGIN_DIR=$(shell python3 -c 'from garmindb import ConfigManager; print(ConfigManager.get_plugins_dir())')
publish_plugins:
	cp ./*_plugin.py $(PLUGIN_DIR)/.

clean_plugins:
	rm -rf $(PLUGIN_DIR)/*.py

republish_plugins: clean_plugins publish_plugins