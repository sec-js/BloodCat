#!/bin/bash
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
import os
import sys
import json
import re
import subprocess
from lib.camlib import *
from lib.log_cat import *

from PyQt5.QtCore import (
    Qt, QUrl, QTimer, QObject, pyqtSlot, QThread, pyqtSignal,
    QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
log = LogCat()
cam = CamLib()

HTML = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>BloodCat Map @ S-H4CK13</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
html, body, #map {
    height: 100%;
    margin: 0;
    padding: 0;
    background-color: #000;
}


.cursor-map {
    cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="24"><text x="0" y="18" font-size="18" fill="lime" font-weight="bold">[ ]</text></svg>') 12 12, auto !important;
}

.cursor-marker,
.cursor-marker:hover {
    cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="24"><text x="0" y="18" font-size="18" fill="lime" font-weight="bold">[+]</text></svg>') 12 12, pointer !important;
}

.ip-tooltip{
    background: rgba(0,0,0,0.78);
    color: #fff;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 6px;
    pointer-events: none;
}

.leaflet-marker-icon { 
    pointer-events: auto;
}


#searchBox { position:absolute; top:10px; right:10px; z-index:9999; background:rgba(0,0,0,0.7); color:#fff; padding:6px; border-radius:6px; width:220px; font-family:"Segoe UI", Arial, sans-serif;}
#searchInput { width:100%; padding:4px 6px; border-radius:4px; border:none; outline:none; background:#222; color:#0f0;}
#searchResults { max-height:150px; overflow-y:auto; margin-top:4px; font-size:12px;}
.searchItem { padding:4px; cursor:pointer;}
.searchItem:hover { background: rgba(0,255,0,0.2); }
</style>
</head>
<body>

<div id="map" class="cursor-map"></div>

<div id="searchBox">
    <input type="text" id="searchInput" placeholder="Search IP / ASN / Network"/>
    <div id="searchResults"></div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script>

const map = L.map('map').setView([20,0],2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);


const icon_main = L.icon({iconUrl:'./location/main.png', iconSize:[32,32], iconAnchor:[16,32]});
const icon_main2 = L.icon({iconUrl:'./location/main2.png', iconSize:[32,32], iconAnchor:[16,32]});


const markers = {}; 
const rtspMap = {}; 
let dataStore = {}; 


let bridge = null;
new QWebChannel(qt.webChannelTransport, function(channel){
    bridge = channel.objects.bridge;
    console.log('WebChannel initialized, bridge=', bridge);
});


function decorateMarkerCursor(m){
    setTimeout(() => {
        try{
            const el = m.getElement();
            if (!el) return;

            el.classList.add('cursor-marker');
            const imgs = el.getElementsByTagName('img');
            for (let i = 0; i < imgs.length; i++) imgs[i].classList.add('cursor-marker');
        }catch(e){}
    }, 0);
}


function updateMarkers(data_obj){
    dataStore = data_obj || {};

    for (let ip in markers){
        if (!(ip in dataStore)){
            map.removeLayer(markers[ip]);
            delete markers[ip];
            delete rtspMap[ip];
        }
    }


    for (let ip in dataStore){
        const item = dataStore[ip];
        const parts = ('' + item.lalo).split(',').map(x => parseFloat(x));
        if (parts.length < 2 || isNaN(parts[0]) || isNaN(parts[1])) continue;
        const coords = [parts[0], parts[1]];
        rtspMap[ip] = item.rtsp;

        let chosenIcon = icon_main;
        if (item.icon && item.icon.indexOf('main2.png') !== -1) chosenIcon = icon_main2;

        if (markers[ip]){
            markers[ip].setLatLng(coords);
        } else {
            const m = L.marker(coords, {icon: chosenIcon}).addTo(map);
            markers[ip] = m;

        const infoHtml = `${ip}<br>${item.sys_org || ''}<br>ASN: ${item.asn || ''}<br>${item.network || ''}`;
        m.bindTooltip(infoHtml, {
            permanent: false,
            direction: 'top',
            offset: [0, -35],
            className: 'ip-tooltip'
        });
            m.bindPopup(infoHtml);

            decorateMarkerCursor(m);

            m.on('mouseover', () => {
                const el = m.getElement();
                if (el) el.classList.add('cursor-marker');
            });
            m.on('mouseout', () => {
            });

    
            m.on('click', () => {
                if (bridge && bridge.playRTSP){
                    try { bridge.playRTSP(item.rtsp); }
                    catch(e){ console.error('bridge.playRTSP error', e); }
                } else {
                    console.warn('bridge not ready');
                }
            });
        }
    }
}

 
const input = document.getElementById('searchInput');
const resultsDiv = document.getElementById('searchResults');

input.addEventListener('input', function(){
    const query = this.value.toLowerCase();
    resultsDiv.innerHTML = '';
    if (!query) return;

    for (let ip in dataStore){
        const item = dataStore[ip];
        const text = `${ip} ${item.asn || ''} ${item.network || ''}`.toLowerCase();
        if (text.includes(query)){
            const div = document.createElement('div');
            div.className = 'searchItem';
            div.textContent = `${ip} | ${item.asn || ''} | ${item.network || ''}`;
            div.onclick = function(){
                const parts = ('' + item.lalo).split(',').map(x=>parseFloat(x));
                if (parts.length >= 2) map.setView([parts[0], parts[1]], 10);
                resultsDiv.innerHTML = ''; input.value = '';
            };
            resultsDiv.appendChild(div);
        }
    }
});
</script>
</body>
</html>
'''

LOGO = "\033[38;5;208m"+r'''
                                               .--.
                                               `.  \
                                                 \  \
                                                  .  \
                                                  :   .
                                                  |    .
                                                  |    :
                                                  |    |
  ..._  ___                                       |    |
 `."".`---'""--..___                              |    |
 ,-\  \             ""-...__         _____________/    |
 / ` " '                    `""""""""                  .
 \                                                      L
 (>                                                      \
/                                                         \
\_    ___..---.                                            L
  `--'         '.                                           \
                 .                                           \_
                _/`.                                           `.._
             .'     -.                                             `.
            /     __.-Y     /''''''-...___,...--------.._            |
           /   _."    |    /                ' .      \   '---..._    |
          /   /      /    /                _,. '    ,/           |   |
          \_,'     _.'   /              /''     _,-'            _|   |
                  '     /               `-----''               /     |
                  `...-'                                       `...
[Maptnh@S-H4CK13]      [Blood Cat V2.2 Map]    [https://github.com/MartinxMax]'''+"\033[0m"


class Bridge(QObject):
    @pyqtSlot(str)
    def playRTSP(self, url):
        ffplay_bin = r'.\lib\ffplay.exe' if sys.platform.startswith('win') else 'ffplay'
        match = re.search(r'@([\d\.]+):', url)
        ip = match.group(1) if match else 'N/A'
        try:
            subprocess.Popen(
                [ffplay_bin, '-rtsp_transport', 'tcp', '-x', '420', '-y', '340', url, '-window_title', ip],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False
            )
            print(f"[+] Playing...")
        except FileNotFoundError:
            print("\033[31m[!] ffplay not found, please install ffmpeg \033[0m")
        except Exception as e:
            print("\033[31m[!] Playback error:", e, "\033[0m")

class DataLoader(QThread):
    remoteLoaded = pyqtSignal(dict)
    localLoaded = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    def parse_raw_to_dict(self, raw, source_label):
        result = {}
        if not raw:
            return result

        def process_obj(obj):
            try:
                rtsp = obj.get("rtsp", "") if isinstance(obj, dict) else ""
                data_obj = obj.get("data", {}) if isinstance(obj, dict) else {}
                lalo = data_obj.get("lalo", "") if isinstance(data_obj, dict) else data_obj.get("lalo", "") if isinstance(data_obj, dict) else ""
                sys_org = data_obj.get("sys_org", "") if isinstance(data_obj, dict) else ""
                asn = data_obj.get("asn", "") if isinstance(data_obj, dict) else ""
                network = data_obj.get("network", "") if isinstance(data_obj, dict) else ""
            except Exception:
                rtsp = ""; lalo = ""; sys_org = ""; asn = ""; network = ""
            m = re.search(r'@([\d\.]+):?', rtsp)
            if m and lalo:
                ip = m.group(1)
                icon_path = "./location/main2.png" if source_label == 'local' else "./location/main.png"
                result[ip] = {
                    "rtsp": rtsp,
                    "lalo": lalo,
                    "sys_org": sys_org,
                    "asn": asn,
                    "network": network,
                    "source": source_label,
                    "icon": icon_path
                }

        if isinstance(raw, str):
            for line in raw.splitlines():
                line = line.strip()
                if not line: continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        process_obj(obj)
                except Exception:
                    continue
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    process_obj(item)
                else:
                    try:
                        obj = json.loads(item)
                        if isinstance(obj, dict):
                            process_obj(obj)
                    except Exception:
                        continue
        else:
            if isinstance(raw, dict):
                process_obj(raw)
            else:
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        process_obj(parsed)
                except Exception:
                    pass

        return result

    def run(self):
        try:
            remote_raw = cam.get_DB_data()
        except Exception as e:
            log.error("cam.get_DB_data() error: %s" % str(e))
            remote_raw = None

        remote_dict = self.parse_raw_to_dict(remote_raw, 'remote')
        self.remoteLoaded.emit(remote_dict)

        try:
            local_raw = cam.get_LocalDB_data()
        except Exception as e:
            log.error("cam.get_LocalDB_data() error: %s" % str(e))
            local_raw = None

        local_dict = self.parse_raw_to_dict(local_raw, 'local')
        self.localLoaded.emit(local_dict)

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BloodCat Map @ S-H4CK13    [https://github.com/MartinxMax]")
        self.resize(1280, 800)

        icon_path = os.path.join(os.path.dirname(__file__), "location", "ico.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.view = QWebEngineView()
        self.layout.addWidget(self.view)

        self.wait_label = QLabel(self)
        self.wait_label.setAlignment(Qt.AlignCenter)
        self.wait_label.setStyleSheet("background-color: rgba(0,0,0,1);")
        self.wait_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.wait_label.setAttribute(Qt.WA_NoSystemBackground) 
        self.wait_label.setCursor(Qt.BlankCursor)
        wait_path = os.path.join(os.path.dirname(__file__), "location", "wait.png")
        self.wait_pixmap = None
        if os.path.exists(wait_path):
            self.wait_pixmap = QPixmap(wait_path)
            self._update_wait_pixmap()
        else:
            print(f"\033[31m[!] No found background: {wait_path}\033[0m")

        self.wait_label.raise_()
        self.wait_label.show()
        self.html_path = os.path.join(os.path.dirname(__file__), "map_temp.html")
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write(HTML)
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(self.channel)

        self.last_data = {}
        self.remote_data = {}  
        self.local_data = {}
        self.merged_data = {}  #

        self.view.loadFinished.connect(self.on_load_finished)
        self.view.load(QUrl.fromLocalFile(os.path.abspath(self.html_path)))

    def _update_wait_pixmap(self):
        if not self.wait_pixmap:
            self.wait_label.setFixedSize(self.size())
            return
        scaled = self.wait_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.wait_label.setPixmap(scaled)
        self.wait_label.setGeometry(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_wait_pixmap()

    def _stop_current_animation(self):
        try:
            if hasattr(self, 'anim_group') and self.anim_group:
                self.anim_group.stop()
        except Exception:
            pass

    def _setup_wait_animation(self, loop=True, loop_count=-1):
        self._stop_current_animation()

        self._opacity_effect = QGraphicsOpacityEffect(self.wait_label)
        self.wait_label.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)

        anim1 = QPropertyAnimation(self._opacity_effect, b"opacity")
        anim1.setDuration(1500)
        anim1.setStartValue(1.0)
        anim1.setEndValue(0.2)
        anim1.setEasingCurve(QEasingCurve.InOutSine)

        anim2 = QPropertyAnimation(self._opacity_effect, b"opacity")
        anim2.setDuration(1500)
        anim2.setStartValue(0.2)
        anim2.setEndValue(1.0)
        anim2.setEasingCurve(QEasingCurve.InOutSine)

        anim3 = QPropertyAnimation(self._opacity_effect, b"opacity")
        anim3.setDuration(1000)
        anim3.setStartValue(1.0)
        anim3.setEndValue(0.0)
        anim3.setEasingCurve(QEasingCurve.InOutQuad)
        anim3.finished.connect(lambda: [
            self.wait_label.hide(),
             self.view.raise_()
        ])

        if not self.wait_label.isVisible():
            self.wait_label.show()

        if loop:
            loop_group = QSequentialAnimationGroup()
            loop_group.addAnimation(anim1)
            loop_group.addAnimation(anim2)
            loop_group.setLoopCount(loop_count)
            loop_group.finished.connect(lambda: anim3.start())
            loop_group.start()
            self.anim_group = loop_group
        else:
            seq = QSequentialAnimationGroup()
            seq.addAnimation(anim1)
            seq.addAnimation(anim2)
            seq.addAnimation(anim3)
            seq.start()
            self.anim_group = seq

    def on_load_finished(self, ok):
        if not ok:
            print("\033[31m[!] BloodCat config file load failed... please check your network...\033[0m")
            return
        self.start_data_loader()

    def start_data_loader(self):
        self.loader = DataLoader()
        self.loader.remoteLoaded.connect(self._handle_remote_loaded)
        self.loader.localLoaded.connect(self._handle_local_loaded)
        self.loader.start()

    def _run_update_js(self, data_dict):
        try:
            js = "updateMarkers(%s);" % json.dumps(data_dict, ensure_ascii=False)
            self.view.page().runJavaScript(js)
        except Exception as e:
            print("\033[31m[!] runJavaScript failed:", e, "\033[0m")

    def _handle_remote_loaded(self, remote_dict):
        log.info("Remote loaded: %d items" % len(remote_dict))
        self.remote_data = remote_dict or {}
        self.merged_data = dict(self.remote_data) 
        self._run_update_js(self.merged_data)
        self._setup_wait_animation(loop=True, loop_count=2)
      

    def _handle_local_loaded(self, local_dict):
        log.info("Local loaded: %d items" % len(local_dict))
        self.local_data = local_dict or {}
        merged = dict(self.remote_data) 
        for ip, local_item in (self.local_data.items() if self.local_data else {}):
            if ip in merged:
                remote_item = merged[ip]
                lalo_to_use = remote_item.get("lalo", "")
                icon_to_use = remote_item.get("icon", "./location/main.png")
                merged[ip] = {
                    "rtsp": local_item.get("rtsp", remote_item.get("rtsp", "")),
                    "lalo": lalo_to_use,
                    "sys_org": local_item.get("sys_org", remote_item.get("sys_org", "")),
                    "asn": local_item.get("asn", remote_item.get("asn", "")),
                    "network": local_item.get("network", remote_item.get("network", "")),
                    "source": "local",
                    "icon": icon_to_use
                }
            else:
                merged[ip] = local_item
        self.merged_data = merged
        self._run_update_js(self.merged_data)

 
if __name__ == "__main__":
    print(LOGO)
    app = QApplication(sys.argv)
    win = MapWindow()
    win.showMaximized()
    sys.exit(app.exec_())
