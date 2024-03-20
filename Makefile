

PLUGIN_DIR=$(shell python3 -c 'from garmindb import GarminConnectConfigManager; gc_config = GarminConnectConfigManager(); print(gc_config.get_plugins_dir())')
publish_plugins:
	cp ./*_plugin.py $(PLUGIN_DIR)/.

clean_plugins:
	rm -rf $(PLUGIN_DIR)/*.py

republish_plugins: clean_plugins publish_plugins

merge_develop:
	git fetch --all && git merge remotes/origin/develop

.PHONY: publish_plugins clean_plugins republish_plugins merge_develop
