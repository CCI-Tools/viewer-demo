const electron = require('electron');
const app = electron.app;  // Module to control application life.
const BrowserWindow = electron.BrowserWindow;  // Module to create native browser window.
const Menu = electron.Menu;  // Module to create native browser window.
const dialog = electron.dialog;  // Module to create native browser window.
const appMenu = require('./app-menu.js');
const path = require('path');

const ipc = electron.ipcMain;

electron.crashReporter.start({
    productName: 'CCI Toolbox',
    companyName: 'ESA',
    submitUrl: 'https://www.brockmann-consult.de/ccitbxws/Crash',
    autoSubmit: true
});

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
var mainWindow = null;

app.preferences = {};

function _openDataFile(filePath) {
    mainWindow.webContents.send('open-data-file', filePath);
}

function _closeDataFile() {
    mainWindow.webContents.send('close-data-file');
}

app.openDataFile = function (window) {
    var filePaths = dialog.showOpenDialog({
        title: 'Open Data File(s)',
        defaultPath: app.preferences.lastDir || null,
        filters: [
            {name: 'NetCDF Files', extensions: ['nc']},
            {name: 'HDF Files', extensions: ['hdf', 'h5']},
            {name: 'ESRI Shapefiles', extensions: ['shp']},
            {name: 'GeoJSON Files', extensions: ['geojson', 'json']},
            {name: 'Google Earth Files', extensions: ['kmz', 'kml']},
            {name: 'GML Files', extensions: ['gml']},
            {name: 'Cesium Files', extensions: ['czml']},
            {name: 'Image Files', extensions: ['jpg', 'png', 'gif', 'tiff']},
            {name: 'All Files', extensions: ['*']}
        ],
        properties: ['openFile']
    });
    if (filePaths && filePaths.length > 0) {
        var filePath = filePaths[0];
        app.preferences.lastDir = path.dirname(filePath);
        console.log('Selected file: ' + filePath);
        if (filePath.endsWith('.nc') || filePath.endsWith('.hdf') || filePath.endsWith('.h5')) {
            _openDataFile(filePath);
        } else {
            dialog.showErrorBox('Unsupported Data File Format', 'Sorry, the CCI Toolbox does not yet understand this data file type.');
        }
    }
};

app.closeDataFile = function (window) {
    _closeDataFile();
};


var menu = Menu.buildFromTemplate(appMenu.create());
Menu.setApplicationMenu(menu);


// Quit when all windows are closed.
app.on('window-all-closed', function () {
    // On OS X it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform != 'darwin') {
        app.quit();
    }
});


// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.on('ready', function () {
    var dataFilesToOpen = [];
    var programOptions = [];
    for (var i in process.argv) {
        var argv = process.argv[i];
        console.log("process.argv[" + i + "] = " + argv);
        if (i >= 2) {
            if (argv.startsWith('-')) {
                programOptions.push(argv);
            } else {
                dataFilesToOpen.push(argv);
            }
        }
    }

    // Create the browser window.
    mainWindow = new BrowserWindow({
        width: 1200, height: 600,
        icon: __dirname + '/images/cci-logo.png',
        //#enable-gpu-rasterization
        webPreferences: {
            // This is the default in Electron 0.36, but it ay change. So fix it here.
            webgl: true
        }

    });

    // and load the index.html of the app.
    mainWindow.loadURL('file://' + __dirname + '/index.html');

    // Open the DevTools.
    mainWindow.webContents.openDevTools();

    // Open data files passed on the command line: electron . {<data-file>}, e.g.:
    // electron . D:\EOData\CCI-TBX\occci-v2.0\geographic\netcdf\monthly\chlor_a\2013\ESACCI-OC-L3S-CHLOR_A-MERGED-1M_MONTHLY_4km_GEO_PML_OC4v6-201302-fv2.0.nc
    mainWindow.webContents.on('did-finish-load', function () {
        for (var i in dataFilesToOpen) {
            var dataFilePath = dataFilesToOpen[i];
            console.log('open ' + dataFilePath);
            _openDataFile(dataFilePath);
        }
    });

    // Emitted when the window is closed.
    mainWindow.on('closed', function () {
        // Dereference the window object, usually you would store windows
        // in an array if your app supports multi windows, this is the time
        // when you should delete the corresponding element.
        mainWindow = null;
    });
});

ipc.on('handle-error', function (event, msg) {
    dialog.showErrorBox('Error', msg);
});
