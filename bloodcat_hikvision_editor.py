#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝

import sys
import csv
import re
import os
import json
import ipaddress
from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from lib.location import Location
from PyQt5.QtWebEngineWidgets import QWebEngineView

DEBUG_GEO = False

LOGO = r'''
             *     ,MMM8&amp;&amp;&amp;.            *
                  MMMM88&amp;&amp;&amp;&amp;&amp;    .
                 MMMM88&amp;&amp;&amp;&amp;&amp;&amp;&amp;
     *           MMM88&amp;&amp;&amp;&amp;&amp;&amp;&amp;&amp;
                 MMM88&amp;&amp;&amp;&amp;&amp;&amp;&amp;&amp;
                 'MMM88&amp;&amp;&amp;&amp;&amp;&amp;'
                   'MMM8&amp;&amp;&amp;'      *    _
          |\___/|                      \\
          )     (    |\_/|              ||    '
         =\     /=   )a a '._.-""""-.  //
           )===(    =\T_= /    ~  ~  \//
          /     \     `"`\   ~   / ~  /
          |     |         |~   \ |  ~/
         /       \         \  ~/- \ ~\
         \       /         || |  // /`
  aac_/\_/\_   _/_/\_/\_/\_((_|\((_//\_/\_/\_
  |  |  |  |( (  |  |  |  |  |  |  |  |  |  |
  |  |  |  | ) ) |  |  |  |  |  |  |  |  |  |
  |  |  |  |(_(  |  |  |  |  |  |  |  |  |  |      
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
Maptnh@S-H4CK13   Bloodcat Hikvision csv Editor  https://github.com/MartinxMax'''


HTML = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>BloodCat Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
html, body, #map { height: 100%; margin:0; padding:0; background-color:#000; }
.cursor-map { cursor: auto !important; }
.ip-tooltip{ background: rgba(0,0,0,0.78); color:#fff; font-size:12px; padding:6px 10px; border-radius:6px; pointer-events: none; }
#searchBox { position:absolute; top:10px; right:10px; z-index:9999; background:rgba(0,0,0,0.7); color:#fff; padding:6px; border-radius:6px; width:260px; font-family:"Segoe UI", Arial, sans-serif; }
#searchInput { width:100%; padding:6px; border-radius:4px; border:none; outline:none; background:#222; color:#0f0;}
#searchResults { max-height:200px; overflow-y:auto; margin-top:6px; font-size:12px;}
.searchItem { padding:6px; cursor:pointer; color:#0f0; border-radius:4px; }
.searchItem:hover { background: rgba(0,255,0,0.08); }
</style>
</head>
<body>
<div id="map" class="cursor-map"></div>

<div id="searchBox">
    <input type="text" id="searchInput" placeholder="Search IP / ASN / Network / Org" />
    <div id="searchResults"></div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
let map = L.map('map').setView([20,0],2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; OSM & CARTO',
    subdomains:'abcd', maxZoom:19
}).addTo(map);

let markers = {}, dataStore = {};
const iconCache = {};
function getIconForPath(path){
    if(!path) return null;
    if(iconCache[path]) return iconCache[path];
    try{
        const ic = L.icon({
            iconUrl: path,
            iconSize: [28,28],
            iconAnchor: [14,28],
            popupAnchor: [0,-26]
        });
        iconCache[path] = ic;
        return ic;
    } catch(e){
        console.warn('getIconForPath failed', path, e);
        return null;
    }
}

function updateMarkers(data_obj){
    dataStore = data_obj || {};
    for(let ip in markers){
        if(!(ip in dataStore)){
            try { map.removeLayer(markers[ip]); } catch(e){}
            delete markers[ip];
        }
    }
    for(let ip in dataStore){
        const item = dataStore[ip];
        const parts = (''+item.lalo).split(',').map(x=>parseFloat(x));
        if(parts.length < 2 || isNaN(parts[0]) || isNaN(parts[1])) continue;
        const coords = [parts[0], parts[1]];
        let chosenIcon = null;
        if(item.icon){
            chosenIcon = getIconForPath(item.icon);
        }
        const markerOptions = {};
        if(chosenIcon) markerOptions.icon = chosenIcon;

        if(markers[ip]){
            markers[ip].setLatLng(coords);
            try { if(chosenIcon) markers[ip].setIcon(chosenIcon); } catch(e){}
        } else {
            const m = L.marker(coords, markerOptions).addTo(map);
            markers[ip] = m;
            const infoHtml = `${ip}<br>${item.sys_org||''}<br>ASN: ${item.asn||''}<br>${item.network||''}`;
            m.bindTooltip(infoHtml, {permanent:false, direction:'top', offset:[0,-35], className:'ip-tooltip'});
            m.bindPopup(infoHtml);
        }
    }
    const q = document.getElementById('searchInput').value.trim().toLowerCase();
    if(q) renderSearchResults(q);
}

function renderSearchResults(q){
    q = (q||'').toLowerCase();
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';
    if(!q) return;
    for(let ip in dataStore){
        try{
            const it = dataStore[ip];
            const text = `${ip} ${it.asn||''} ${it.network||''} ${it.sys_org||''}`.toLowerCase();
            if(text.includes(q)){
                const div = document.createElement('div');
                div.className = 'searchItem';
                div.textContent = ip + (it.sys_org ? ' - ' + it.sys_org : '');
                div.onclick = (ev) => {
                    if(markers[ip]){
                        const latlng = markers[ip].getLatLng();
                        map.setView(latlng, 9);
                        markers[ip].openPopup();
                    } else {
                        const parts = (''+it.lalo).split(',').map(x=>parseFloat(x));
                        if(parts.length>=2 && !isNaN(parts[0]) && !isNaN(parts[1])){
                            map.setView([parts[0], parts[1]], 9);
                        }
                    }
                };
                resultsDiv.appendChild(div);
            }
        }catch(e){}
    }
}

document.getElementById('searchInput').addEventListener('input', function(){
    const q = this.value.trim().toLowerCase();
    renderSearchResults(q);
});
</script>
</body>
</html>
'''

class MapDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, markers_data=None):
        super().__init__(parent)

        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        self.setSizeGripEnabled(True)
        try:
            screen = QtWidgets.QApplication.primaryScreen()
            geo = screen.availableGeometry()
            w = int(geo.width() * 2 / 3)
            h = int(geo.height() * 2 / 3)
            x = geo.x() + (geo.width() - w) // 2
            y = geo.y() + (geo.height() - h) // 2
            self.setGeometry(x, y, w, h)
        except Exception:
            self.resize(1000, 700)

        self.setWindowTitle("Bloodcat Hikvision Map")

        layout = QtWidgets.QVBoxLayout(self)

        if QWebEngineView is None:
            label = QtWidgets.QLabel("PyQtWebEngine is not installed, map cannot be displayed.")
            layout.addWidget(label)
            return

        self.view = QWebEngineView(self)
        layout.addWidget(self.view)

        base = QUrl.fromLocalFile(os.getcwd() + os.sep)
        self.view.setHtml(HTML, base)

        def on_load(ok):
            if ok:
                data = markers_data or {}
                js_data = json.dumps(data, ensure_ascii=False)
                self.view.page().runJavaScript(f"updateMarkers({js_data});")
            else:
                print("Map page failed to load")
        self.view.loadFinished.connect(on_load)

class HikEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bloodcat Hikvision Editor")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(base_dir, 'location', 'ico.png')
        if os.path.isfile(ico_path):
            self.setWindowIcon(QtGui.QIcon(ico_path))

        self.data = []
        self.headers = []
        self.current_delimiter = ','
        self.geo_field_name = '__geo_country'
        self.geo_full_field = '__geo_full'

        self.geo = None
        self.geo_cache = {}
        if Location:
            try:
                self.geo = Location()
                print("[+] Location initialized")
            except Exception as e:
                print("[-] Location init failed:", e)
                self.geo = None

        self._build_ui()

    def is_public_ip(self, ip):
        try:
            return ipaddress.ip_address(ip).is_global
        except Exception:
            return False

    def extract_ip(self, text):
        if not text:
            return ''
        s = text.strip()
        m = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', s)
        if m:
            return m.group(1)
        return ''

    def fetch_geo_full(self, ip):
        if not self.geo or not ip:
            return {}
        clean_ip = self.extract_ip(ip)
        if not clean_ip:
            return {}
        if not self.is_public_ip(clean_ip):
            return {}
        if clean_ip in self.geo_cache:
            return self.geo_cache[clean_ip]
        try:
            data = self.geo.get(clean_ip)
            if isinstance(data, dict):
                self.geo_cache[clean_ip] = data
                return data
        except Exception as e:
            if DEBUG_GEO:
                print("[geo fail]", clean_ip, e)
        self.geo_cache[clean_ip] = {}
        return {}

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_h = QtWidgets.QHBoxLayout(central)
        main_h.setContentsMargins(8,8,8,8)
        main_h.setSpacing(8)

        sidebar = QtWidgets.QFrame()
        sidebar.setMaximumWidth(360)
        sv = QtWidgets.QVBoxLayout(sidebar)
        sv.setSpacing(6)

        self.import_btn = QtWidgets.QPushButton("Import Hikvision camera configuration file")
        self.import_btn.clicked.connect(self.import_csv)
        sv.addWidget(self.import_btn)

        self.export_btn = QtWidgets.QPushButton("Export selected entries")
        self.export_btn.clicked.connect(self.export_selected)
        sv.addWidget(self.export_btn)

        ops_layout = QtWidgets.QHBoxLayout()
        self.btn_select_all = QtWidgets.QPushButton("Select all entries")
        self.btn_select_all.clicked.connect(self.select_all)
        ops_layout.addWidget(self.btn_select_all)
        self.btn_invert = QtWidgets.QPushButton("Invert selection")
        self.btn_invert.clicked.connect(self.invert_selection)
        ops_layout.addWidget(self.btn_invert)
        self.btn_clear = QtWidgets.QPushButton("Clear all selections")
        self.btn_clear.clicked.connect(self.clear_selection)
        ops_layout.addWidget(self.btn_clear)
        sv.addLayout(ops_layout)

        self.btn_delete = QtWidgets.QPushButton("Delete selected entries")
        self.btn_delete.clicked.connect(self.delete_selected_rows)
        sv.addWidget(self.btn_delete)

        self.btn_view_geo = QtWidgets.QPushButton("View actual geographic locations")
        self.btn_view_geo.clicked.connect(self.open_map_dialog)
        sv.addWidget(self.btn_view_geo)

        sv.addStretch()
        main_h.addWidget(sidebar)

        right_frame = QtWidgets.QFrame()
        rh = QtWidgets.QVBoxLayout(right_frame)
        rh.setContentsMargins(0,0,0,0)
        rh.setSpacing(6)

        header_bar = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel('No data loaded')
        header_bar.addWidget(self.status_label)
        header_bar.addStretch()

        self.search_field_cb = QtWidgets.QComboBox()
        self.search_field_cb.setMinimumWidth(180)
        header_bar.addWidget(self.search_field_cb)

        self.search_le = QtWidgets.QLineEdit()
        self.search_le.setPlaceholderText('Enter text to search')
        self.search_le.returnPressed.connect(self.quick_search_apply)
        header_bar.addWidget(self.search_le)

        self.search_btn = QtWidgets.QPushButton('Search')
        self.search_btn.clicked.connect(self.quick_search_apply)
        header_bar.addWidget(self.search_btn)

        self.search_clear_btn = QtWidgets.QPushButton('Clear')
        self.search_clear_btn.clicked.connect(self.quick_search_clear)
        header_bar.addWidget(self.search_clear_btn)

        rh.addLayout(header_bar)

        self.table = QtWidgets.QTableWidget()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.cellDoubleClicked.connect(self.show_row_details)
        rh.addWidget(self.table, 1)

        main_h.addWidget(right_frame, 1)

        self.status = self.statusBar()

    def import_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", os.getcwd(), "CSV/TXT (*.csv *.txt);;All Files (*)")
        if not path:
            return
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        delimiter = ',' if text.count(',') >= text.count('\t') else '\t'
        self.current_delimiter = delimiter
        rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
        if not rows:
            return
        self.headers = [h.strip() for h in rows[0]]
        self.data.clear()
        self.geo_cache.clear()
        for r in rows[1:]:
            r += [''] * (len(self.headers) - len(r))
            od = OrderedDict(zip(self.headers, r))
            ip_candidate = ''
            if len(r) >= 3:
                adding_mode = r[1].strip()
                if adding_mode == '0':
                    ip_candidate = self.extract_ip(r[2])
            if not ip_candidate:
                for k in ['IP','ip','Address','address','Host','host']:
                    if k in od and od[k].strip():
                        ip_candidate = self.extract_ip(od[k].strip())
                        break
            geo_full = {}
            if ip_candidate and self.geo:
                geo_full = self.fetch_geo_full(ip_candidate)
            od[self.geo_full_field] = geo_full
            od[self.geo_field_name] = geo_full.get('country','') if isinstance(geo_full, dict) else ''
            self.data.append(od)
        self.populate_search_field_cb()
        self.refresh_table(self.data)
        self.status_label.setText(f'Loaded {len(self.data)} records')
        self.status.showMessage(f"Loaded {len(self.data)} records", 4000)

    def export_selected(self):
        selected = []
        for r in range(self.table.rowCount()):
            cb = self.table.cellWidget(r,0)
            if cb and cb.isChecked():
                item = self.table.item(r,2)
                if item:
                    od = item.data(QtCore.Qt.UserRole)
                    if isinstance(od, dict):
                        selected.append(od)

        if not selected:
            QtWidgets.QMessageBox.information(self, 'No selection', 'Please check the entries to export first')
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "export.csv")
        if not path:
            return

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.current_delimiter)
            writer.writerow(self.headers)
            for od in selected:
                writer.writerow([od.get(h,'') for h in self.headers])

        self.status.showMessage(f"Exported {len(selected)} entries to {path}", 4000)

    def refresh_table(self, rows):
        self.table.setRowCount(0)
        self.table.setColumnCount(2 + len(self.headers))
        self.table.setHorizontalHeaderLabels(['Sel', 'Country'] + self.headers)

        for r, od in enumerate(rows):
            self.table.insertRow(r)

            cb = QtWidgets.QCheckBox()
            self.table.setCellWidget(r, 0, cb)

            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(
                od.get(self.geo_field_name, '')
            ))

            for c, h in enumerate(self.headers, start=2):
                it = QtWidgets.QTableWidgetItem(od.get(h, ''))
    
                it.setData(QtCore.Qt.UserRole, od)
                self.table.setItem(r, c, it)

        self.table.resizeColumnsToContents()

    def select_all(self):
        for r in range(self.table.rowCount()):
            w = self.table.cellWidget(r,0)
            if isinstance(w, QtWidgets.QCheckBox):
                w.setChecked(True)
        self.status.showMessage('All selected', 2000)

    def invert_selection(self):
        for r in range(self.table.rowCount()):
            w = self.table.cellWidget(r,0)
            if isinstance(w, QtWidgets.QCheckBox):
                w.setChecked(not w.isChecked())
        self.status.showMessage('Inverted selection', 2000)

    def clear_selection(self):
        for r in range(self.table.rowCount()):
            w = self.table.cellWidget(r,0)
            if isinstance(w, QtWidgets.QCheckBox):
                w.setChecked(False)
        self.status.showMessage('Cleared all selections', 2000)

    def delete_selected_rows(self):
        to_remove = []
        for r in range(self.table.rowCount()):
            cb = self.table.cellWidget(r, 0)
            if cb and cb.isChecked():
                item = self.table.item(r, 2)
                if item:
                    od = item.data(QtCore.Qt.UserRole)
                    if isinstance(od, dict):
                        to_remove.append(od)

        if not to_remove:
            QtWidgets.QMessageBox.information(self, 'No selection', 'Please check the entries to delete first')
            return

        if QtWidgets.QMessageBox.question(
            self, 'Confirm deletion',
            f'Will delete {len(to_remove)} records from the table, continue?'
        ) != QtWidgets.QMessageBox.Yes:
            return

        for od in to_remove:
            if od in self.data:
                self.data.remove(od)

        self.refresh_table(self.data)
        self.status.showMessage(f'Deleted {len(to_remove)} records', 4000)

    def populate_search_field_cb(self):
        self.search_field_cb.clear()
        self.search_field_cb.addItem("Country")
        self.search_field_cb.addItems(self.headers)

    def quick_search_apply(self):
        q = self.search_le.text().strip()
        field = self.search_field_cb.currentText()
        if q == '':
            self.refresh_table(self.data)
            self.status.showMessage('Search cleared, showing all', 2000)
            return
        q_low = q.lower()
        matched = []
        for od in self.data:
            if field == "Country":
                cell = od.get(self.geo_field_name, '') or ''
            else:
                cell = od.get(field, '') or ''
            if q_low in str(cell).lower():
                matched.append(od)
        self.refresh_table(matched)
        self.status.showMessage(f'Search matched {len(matched)} entries', 4000)

    def quick_search_clear(self):
        self.search_le.clear()
        self.refresh_table(self.data)
        self.status.showMessage('Search cleared, showing all', 2000)

    def show_row_details(self, row, col):
        item = self.table.item(row, 2)
        if not item:
            return

        od = item.data(QtCore.Qt.UserRole)
        if not isinstance(od, dict):
            return

        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Edit Entry")
        v = QtWidgets.QVBoxLayout(dlg)

        country = od.get(self.geo_field_name, '')
        if country:
            v.addWidget(QtWidgets.QLabel(f"Country: {country}"))

        form = QtWidgets.QFormLayout()
        edits = {}
        for h in self.headers:
            le = QtWidgets.QLineEdit(od.get(h, ''))
            edits[h] = le
            form.addRow(h, le)
        v.addLayout(form)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        v.addWidget(btns)

        if dlg.exec_():
            for h, le in edits.items():
                od[h] = le.text()
 
            ip_candidate = self.extract_ip(
                od.get(self.headers[2], '')
            ) if len(self.headers) >= 3 else ''

            geo_full = {}
            if ip_candidate and self.geo:
                geo_full = self.fetch_geo_full(ip_candidate)

            od[self.geo_full_field] = geo_full
            od[self.geo_field_name] = geo_full.get('country', '')

            self.refresh_table(self.data)
            self.status.showMessage('Entry saved', 2000)

    def open_map_dialog(self):
        if QWebEngineView is None:
            QtWidgets.QMessageBox.warning(self, 'Missing component', 'PyQtWebEngine not detected, cannot open map.')
            return
        selected = []
        for r in range(self.table.rowCount()):
            cb = self.table.cellWidget(r,0)
            if cb and cb.isChecked():
                item = self.table.item(r,2)
                if item:
                    idx = item.data(QtCore.Qt.UserRole)
                    if isinstance(idx, int):
                        selected.append(self.data[idx])
        if selected:
            source_list = selected
        else:
            source_list = [od for od in self.data if od.get(self.geo_full_field) and od.get(self.geo_full_field).get('lalo')]
        if not source_list:
            QtWidgets.QMessageBox.information(self, 'Map start failed', 'Please import a CSV file first')
            return
        markers_data = {}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_filename = os.path.join(script_dir, 'location', 'color_1.png')
        icon_url = ''
        if os.path.isfile(icon_filename):
            icon_url = QUrl.fromLocalFile(icon_filename).toString()
        else:
            alt = os.path.join(script_dir, 'location', 'ico.png')
            if os.path.isfile(alt):
                icon_url = QUrl.fromLocalFile(alt).toString()

        for od in source_list:
            ip = ''
            if len(self.headers) >= 3:
                adding_mode_val = od.get(self.headers[1], '').strip()
                if adding_mode_val == '0':
                    ip = self.extract_ip(od.get(self.headers[2], ''))
            if not ip:
                for k in ['IP','ip','Address','address','Host','host','Name']:
                    if k in od and od[k].strip():
                        ip = self.extract_ip(od[k].strip())
                        if ip:
                            break
            geo = od.get(self.geo_full_field) or {}
            lalo = geo.get('lalo') or geo.get('latlng') or geo.get('lat_lon') or ''
            if isinstance(lalo, (list,tuple)) and len(lalo) >= 2:
                lalo = f"{lalo[0]},{lalo[1]}"
            if not lalo:
                lat = geo.get('lat') or geo.get('latitude') or ''
                lng = geo.get('lon') or geo.get('lng') or geo.get('longitude') or ''
                if lat and lng:
                    lalo = f"{lat},{lng}"
            if not lalo:
                continue
            item = {
                'lalo': str(lalo),
                'asn': geo.get('asn',''),
                'sys_org': geo.get('sys_org','') or od.get('User Name','') or od.get('User','') or '',
                'network': geo.get('network',''),
                'rtsp': od.get('Address','') or od.get('address','') or '',
                'icon': icon_url,
                'source_url': ''
            }
            key = ip or (od.get(self.headers[0]) or f"row{item.data(QtCore.Qt.UserRole)}")
            markers_data[key] = item

        dlg = MapDialog(self, markers_data)
        dlg.exec_()

if __name__ == "__main__":
    print(LOGO)
    app = QtWidgets.QApplication(sys.argv)
    win = HikEditor()
    win.showMaximized()
    sys.exit(app.exec_())
