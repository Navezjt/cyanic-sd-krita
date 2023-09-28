from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDoubleValidator
from ..sdapi_v1 import SDAPI
from ..settings_controller import SettingsController

class SettingsPage(QWidget):
    def __init__(self, settings_controller:SettingsController, api:SDAPI):
        super().__init__()
        self.settings_controller = settings_controller
        self.api = api
        self.connected = False

        self.setLayout(QVBoxLayout())
        self._server_settings_group()
        # self._generation_group()
        self._previews_group()
        self._prompt_group()
        self.layout().addStretch() # Takes up the remaining space at the bottom, allowing everything to be pushed to the top


    def _server_settings_group(self):
        host_form = QGroupBox('Server Settings')
        host_form.setLayout(QFormLayout())
        host_addr = QLineEdit(self.settings_controller.get('server.host'))
        host_addr.setPlaceholderText(self.api.DEFAULT_HOST)
        host_form.layout().addRow('Host', host_addr)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(lambda: self.test_new_host(host_addr.text()))
        host_form.layout().addWidget(connect_btn)
        self.connection_label = QLabel()
        host_form.layout().addWidget(self.connection_label)

        host_form.layout().addRow('Save images on host', self.create_checkbox('server.save_imgs'))
        self.add_tooltip(host_form, 'Enable to have the host save generated images, the same way it would in the WebUI.')

        # IDK what server setting to change to toggle this, so it'll have to be server default
        # host_form.layout().addRow('Filter NSFW', self.create_checkbox('server.filter_nsfw'))

        self.layout().addWidget(host_form)


    def _previews_group(self):
        previews_form = QGroupBox('Previews')
        previews_form.setLayout(QFormLayout())

        previews_form.layout().addRow('Show Previews', self.create_checkbox('previews.enabled'))
        self.add_tooltip(previews_form, 'Enable to have preview images generated on the canvas.')

        refresh_time = QLineEdit('%s' % self.settings_controller.get('previews.refresh_seconds'))
        refresh_time.setPlaceholderText('1.0')
        refresh_time.setValidator(QDoubleValidator(0.5, 10.0, 1))
        refresh_time.textChanged.connect(lambda: self.settings_controller.set('previews.refresh_seconds', float(refresh_time.text()) if len(refresh_time.text()) > 0 else 1.0))
        previews_form.layout().addRow('Refresh Time (seconds)', refresh_time)
        self.add_tooltip(previews_form, 'Sets how often Krita asks SD for an update. Progress bar will update faster or slower depending on this setting.')

        self.layout().addWidget(previews_form)


    def _prompt_group(self):
        prompt_form = QGroupBox('Prompts')
        prompt_form.setLayout(QFormLayout())

        prompt_form.layout().addRow('Share Prompts', self.create_checkbox('prompts.share_prompts'))
        self.add_tooltip(prompt_form, 'Share prompt/negative prompt text between Txt2Img, Img2Img, etc.')

        prompt_form.layout().addRow('Save Prompts', self.create_checkbox('prompts.save_prompts'))
        self.add_tooltip(prompt_form, 'Save prompts/negative prompts in Krita\'s UI for next time.')
        self.layout().addWidget(prompt_form)


    def _generation_group(self):
        generation_form = QGroupBox('Generation Settings')
        generation_form.setLayout(QFormLayout())

        generation_form.layout().addRow('Sampler', QComboBox())
        generation_form.layout().addRow('Steps', QSpinBox())
        generation_form.layout().addRow('Model', QComboBox())
        generation_form.layout().addRow('VAE', QComboBox())
        generation_form.layout().addRow('Refiner', QComboBox())
        generation_form.layout().addRow('Upscaler', QComboBox())
        generation_form.layout().addRow('Face Restorer', QComboBox())
        generation_form.layout().addRow('Clip Skip', QSpinBox())
        generation_form.layout().addRow('Batch Count', QSpinBox())
        generation_form.layout().addRow('Batch Size', QSpinBox())
        generation_form.layout().addRow('CFG Scale', QSpinBox())


        self.layout().addWidget(generation_form)


    def update(self):
        super().update()
        self.repaint()


    def add_tooltip(self, form:QWidget, text):
        # Add tooltips to the last 2 items added to the form, which should be the label and the input
        index = len(form.children()) - 2 # layout() is listed as a child, which throws off the count
        form.layout().itemAt(index).widget().setToolTip(text)
        form.layout().itemAt(index - 1).widget().setToolTip(text)


    def get_key_from_value(self, dict, value):
        # The order of keys and values doesn't change unless the dict is modified
        return list(dict.keys())[list(dict.values()).index(value)]
    

    def create_checkbox(self, settings_key):
        cb = QCheckBox()
        cb.setChecked(self.settings_controller.get(settings_key))
        cb.toggled.connect(lambda: self.update_setting(settings_key, cb.isChecked()))
        return cb
    

    def create_combobox(self, options, default, settings_key):
        cb = QComboBox()
        cb.addItems(options)
        cb.setCurrentText(default)
        # cb.eventFilter(self, QtGui.QWheelEvent()) # Would like to filter out scroll wheel changing combobox
        cb.currentIndexChanged.connect(lambda: self.update_setting(settings_key, cb.currentText()))
        return cb
    

    def test_new_host(self, host=''):
        if len(host) == 0: # Check if the host provided in the API is a valid server (or running)
            try:
                self.api.get_status()
                self.connection_label.setText('Connected')
                self.connected = True
            except:
                self.connection_label.setText('No Connection')
                self.connected = False
            return
        # Check a user entered host
        try:
            test_api = SDAPI(host)
            test_api.get_status()
            # Test passed, inform user, update api
            self.connection_label.setText('Connected')
            self.api.change_host(host)
            self.connected = True
        except:
            # Test failed, inform user
            self.connection_label.setText('No Connection')
            self.connected = False


    def update_setting(self, key, value):
        self.settings_controller.set(key, value)


    def save_user_settings(self):
        try:
            self.settings_controller.save()
            self.save_message.setText('Saved settings!')
        except Exception as e:
            self.save_message.setText('Unable to save settings: %s' % e)

