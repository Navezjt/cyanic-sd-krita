import json
import os.path

class SettingsController():
    # Loads and saves settings for the entire plug-in
    def __init__(self):
        self.settings = {}
        self.plugin_dir = os.path.dirname(os.path.realpath(__file__))
        self.user_settings_file = os.path.join(self.plugin_dir, 'user_settings.json')
        self.default_settings_file = os.path.join(self.plugin_dir, 'default_settings.json')
        self.load()

    def load(self):
        # Load default first, then merge in user settings. It's safer for updates that add new settings.
        if os.path.isfile(self.default_settings_file):
            with open(self.default_settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            raise Exception('Cyanic SD - No default settings file found in %s' % self.plugin_dir)
        
        if os.path.isfile(self.user_settings_file):
            user_settings = {}
            with open(self.user_settings_file, 'r') as f:
                user_settings = json.load(f)
            for key in self.settings.keys():
                if key in user_settings:
                    if type(self.settings[key]) == dict:
                        # This assumes there's only one nested dict layer.
                        for sub_key in self.settings[key]:
                            if sub_key in user_settings[key]:
                                self.settings[key][sub_key] = user_settings[key][sub_key]    
                    else:
                        self.settings[key] = user_settings[key]


    def save(self):
        try:
            with open(self.user_settings_file, 'w') as f:
                f.write(json.dumps(self.settings, indent=4))
        except Exception as e:
            raise Exception('Cyanic SD - Error saving user settings: %s' % e)
        
    def restore_defaults(self):
        # Would saving the user settings as "user_settings.old" be better?
        try:
            with open(self.user_settings_file, 'w') as f:
                f.write(json.dumps(self.default_settings_file, indent=4))
        except Exception as e:
            raise Exception('Cyanic SD - Error saving user settings: %s' % e)
    
    # Use 'previews.enabled' as the key for '{"previews": {"enabled": true}}'
    def get(self, key):
        split_key = key.split('.')
        if len(split_key) == 1:
            return self.settings[key]
        if not split_key[0] in self.settings:
            return None
        return self.settings[split_key[0]][split_key[1]]
    
    def set(self, key, value):
        split_key = key.split('.')
        if len(split_key) == 1:
            self.settings[key] = value
        else:
            if not split_key[0] in self.settings:
                self.settings[split_key[0]] = {}
            self.settings[split_key[0]][split_key[1]] = value

    def has_key(self, key):
        split_key = key.split('.')
        if len(split_key) == 1:
            return key in self.settings
        else:
            if not split_key[0] in self.settings:
                return False
            return split_key[1] in self.settings[split_key[0]]