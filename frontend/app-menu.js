var electron = require('electron');

function ifDarwinOrElse(darwinValue, elseValue) {
    if (process.platform == 'darwin')
        return darwinValue;
    else
        return elseValue;
}

exports.create = function () {
    var template = [
        {
            /* index: 0 */
            label: 'File',
            submenu: [
                {
                    label: 'Open Data File',
                    click: electron.app.openDataFile
                },
                {
                    label: 'Close Data File',
                    click: electron.app.closeDataFile
                }
            ]
        },
        {
            /* index: 1 */
            label: 'Edit',
            submenu: [
                {
                    label: 'Undo',
                    accelerator: 'CmdOrCtrl+Z',
                    role: 'undo'
                },
                {
                    label: 'Redo',
                    accelerator: 'Shift+CmdOrCtrl+Z',
                    role: 'redo'
                },
                {
                    type: 'separator'
                },
                {
                    label: 'Cut',
                    accelerator: 'CmdOrCtrl+X',
                    role: 'cut'
                },
                {
                    label: 'Copy',
                    accelerator: 'CmdOrCtrl+C',
                    role: 'copy'
                },
                {
                    label: 'Paste',
                    accelerator: 'CmdOrCtrl+V',
                    role: 'paste'
                },
                {
                    label: 'Select All',
                    accelerator: 'CmdOrCtrl+A',
                    role: 'selectall'
                }
            ]
        },
        {
            /* index: 2 */
            label: 'View',
            submenu: [
                {
                    label: 'Layers',
                    accelerator: ifDarwinOrElse('Ctrl+Command+F3', 'F3'),
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('show-layers-window');
                    }
                },
                {
                    label: 'Layer Properties',
                    accelerator: ifDarwinOrElse('Ctrl+Command+F4', 'F4'),
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('show-layer-properties-window');
                    }
                },
                {
                    label: 'Data Files',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('show-data-files-window');
                    }
                },
                {
                    label: 'Data File Info',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('show-file-info-window');
                    }
                },
                {
                    label: 'Variable Info',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('show-variable-info-window');
                    }
                },
                {
                    label: 'Color Maps',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('show-color-maps-window');
                    }
                },
                {
                    label: 'Time-Series Plot',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('show-time-series-plot-window');
                    }
                },
                {
                    type: 'separator'
                },
                {
                    label: 'Reload',
                    accelerator: 'CmdOrCtrl+R',
                    click: function (item, window) {
                        if (window)
                            window.reload();
                    }
                },
                {
                    label: 'Toggle Full Screen',
                    accelerator: ifDarwinOrElse('Ctrl+Command+F', 'F11'),
                    click: function (item, window) {
                        if (window)
                            window.setFullScreen(!window.isFullScreen());
                    }
                },
                {
                    label: 'Toggle Developer Tools',
                    accelerator: ifDarwinOrElse('Alt+Command+I', 'Ctrl+Shift+I'),
                    click: function (item, window) {
                        if (window)
                            window.toggleDevTools();
                    }
                }
            ]
        },
        {
            /* index: 3 */
            label: 'Tools',
            role: 'tools',
            submenu: [
                {
                    label: 'Add POI',
                    role: 'add_poi',
                    accelerator: 'CmdOrCtrl+P',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('add-point-of-interest');
                    }
                },
                {
                    label: 'Remove POI',
                    role: 'remove_poi',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('remove-point-of-interest');
                    }
                },
                {
                    label: 'Remove All POIs',
                    role: 'remove_all_pois',
                    click: function (item, window) {
                        if (window)
                            window.webContents.send('remove-all-points-of-interest');
                    }
                }
            ]
        },
        {
            /* index: 4 */
            label: 'Window',
            role: 'window',
            submenu: [
                {
                    label: 'Minimize',
                    accelerator: 'CmdOrCtrl+M',
                    role: 'minimize'
                },
                {
                    label: 'Close',
                    accelerator: 'CmdOrCtrl+W',
                    role: 'close'
                }
            ]
        },
        {
            /* index: 5 */
            label: 'Help',
            role: 'help',
            submenu: [
                {
                    label: 'ESA Climate Change Initiative',
                    click: function () {
                        electron.shell.openExternal('http://cci.esa.int/')
                    }
                }
            ]
        }
    ];

    if (process.platform == 'darwin') {

        // Extend Windows menu
        var windowMenu = template[4];
        windowMenu.submenu.push(
            {
                type: 'separator'
            },
            {
                label: 'Bring All to Front',
                role: 'front'
            }
        );

        // Insert Application menu
        template.unshift({
            label: name,
            submenu: [
                {
                    label: 'About ' + electron.app.getName(),
                    role: 'about'
                },
                {
                    type: 'separator'
                },
                {
                    label: 'Preferences...',
                    accelerator: 'Command+,',
                    click: electron.app.openPreferencesWindow
                },
                {
                    type: 'separator'
                },
                {
                    label: 'Services',
                    role: 'services',
                    submenu: []
                },
                {
                    type: 'separator'
                },
                {
                    label: 'Hide ' + electron.app.getName(),
                    accelerator: 'Command+H',
                    role: 'hide'
                },
                {
                    label: 'Hide Others',
                    accelerator: 'Command+Shift+H',
                    role: 'hideothers'
                },
                {
                    label: 'Show All',
                    role: 'unhide'
                },
                {
                    type: 'separator'
                },
                {
                    label: 'Quit ' + electron.app.getName(),
                    accelerator: 'Command+Q',
                    click: function () {
                        electron.app.quit();
                    }
                }
            ]
        });
    } else {
        // Extend File menu
        var fileMenu = template[0];
        fileMenu.submenu.push(
            {
                type: 'separator'
            },
            {
                label: 'Preferences...',
                click: electron.app.openPreferencesWindow
            },
            {
                type: 'separator'
            },
            {
                label: 'Exit',
                click: function () {
                    electron.app.quit();
                }
            }
        );

        // Extend Help menu
        var helpMenu = template[4];
        helpMenu.submenu.push(
            {
                type: 'separator'
            },
            {
                label: 'About...',
                click: function() {}
            }
        );
    }

    return template;
}