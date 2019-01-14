# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
import json
import sys
import textwrap

from QtExt import QtCore, QtWidgets, QtGui


from ftrack_connect.config import get_log_directory
import ftrack_connect.util


class AboutDialog(QtWidgets.QDialog):
    '''About widget.'''

    def __init__(
        self, parent,
        icon=':ftrack/image/default/ftrackLogoLabelDark'
    ):
        super(AboutDialog, self).__init__(parent)
        self.setWindowTitle('About connect')
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(layout)

        self.icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(icon)
        self.icon.setPixmap(
            pixmap.scaledToHeight(25, mode=QtCore.Qt.SmoothTransformation)
        )
        self.icon.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.icon)
        layout.addSpacing(10)

        self.messageLabel = QtWidgets.QLabel()
        self.messageLabel.setWordWrap(True)
        self.messageLabel.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.messageLabel)

        layout.addSpacing(25)

        self.debugButton = QtWidgets.QPushButton('More info')
        self.debugButton.clicked.connect(self._onDebugButtonClicked)

        layout.addWidget(self.debugButton)

        self.loggingButton = QtWidgets.QPushButton('Open log directory')
        self.loggingButton.clicked.connect(self._onLoggingButtonClicked)

        layout.addWidget(self.loggingButton)

        if sys.platform == 'linux2':
            self.createApplicationShortcutButton = QtWidgets.QPushButton(
                'Create application shortcut'
            )
            self.createApplicationShortcutButton.clicked.connect(
                self._onCreateApplicationShortcutClicked
            )
            layout.addWidget(self.createApplicationShortcutButton)

        self.debugTextEdit = QtWidgets.QTextEdit()
        self.debugTextEdit.setReadOnly(True)
        self.debugTextEdit.setFontPointSize(10)
        self.debugTextEdit.hide()
        layout.addWidget(self.debugTextEdit)

    def _onDebugButtonClicked(self):
        '''Handle debug button clicked.'''
        self.debugButton.hide()
        self.debugTextEdit.show()
        self.adjustSize()

    def _onLoggingButtonClicked(self):
        '''Handle logging button clicked.'''
        directory = get_log_directory()

        if not os.path.exists(directory):
            # Create directory if not existing.
            try:
                os.makedirs(directory)
            except OSError:
                messageBox = QtWidgets.QMessageBox(parent=self)
                messageBox.setIcon(QtWidgets.QMessageBox.Warning)
                messageBox.setText(
                    u'Could not open or create logging '
                    u'directory: {0}.'.format(directory)
                )
                messageBox.exec_()
                return

        ftrack_connect.util.open_directory(directory)

    def _onCreateApplicationShortcutClicked(self):
        '''Create a desktop entry for Connect.'''
        if sys.platform != 'linux2':
            return

        if os.path.realpath(__file__).startswith(os.path.expanduser('~')):
            directory = os.path.expanduser('~/.local/share/applications')
        else:
            directory = '/usr/share/applications'
        filepath = os.path.join(directory, 'ftrack-connect-package.desktop')

        if os.path.exists(filepath):
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle('Overwrite file')
            msgBox.setText('{0} already exists.'.format(filepath))
            msgBox.setInformativeText('Do you want to overwrite it?')
            msgBox.setStandardButtons(
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
            ret = msgBox.exec_()
            if ret == QtWidgets.QMessageBox.No:
                return

        application_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        content = textwrap.dedent('''\
        #!/usr/bin/env xdg-open

        [Desktop Entry]
        Type=Application
        Icon={0}/logo.svg
        Name=ftrack connect package
        Comment=ftrack connect package
        Exec={0}/ftrack_connect_package
        StartupNotify=true
        Terminal=false
        '''.format(application_dir))

        with open(filepath, 'w+') as f:
            f.write(content)

        messageBox = QtWidgets.QMessageBox(parent=self)
        messageBox.setText(
            u'Wrote shortcut file to: {0}.'.format(filepath)
        )
        messageBox.exec_()

    def setInformation(self, versionData, user, server):
        '''Set displayed *versionData*, *user*, *server*.'''
        core = [plugin for plugin in versionData if plugin.get('core')]
        plugins = [
            plugin for plugin in versionData if plugin.get('core') is not True
        ]

        coreTemplate = '''
        <h4>Version:</h4>
        <p>{core_versions}</p>
        <h4>Server and user:</h4>
        <p>{server}<br>
        {user}<br></p>
        '''

        itemTemplate = '{name}: {version}<br>'

        coreVersions = ''
        for _core in core:
            coreVersions += itemTemplate.format(
                name=_core['name'],
                version=_core['version']
            )

        content = coreTemplate.format(
            core_versions=coreVersions,
            server=server,
            user=user
        )

        if plugins:
            pluginVersions = ''
            for _plugin in plugins:
                pluginVersions += itemTemplate.format(
                    name=_plugin['name'],
                    version=_plugin['version']
                )

            content += '<h4>Plugins:</h4>{0}'.format(pluginVersions)

        self.messageLabel.setText(content)
        self.debugTextEdit.insertPlainText(
            json.dumps(versionData, indent=4, sort_keys=True)
        )
