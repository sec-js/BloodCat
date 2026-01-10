 

# Blood-Cat

A tool for hacking into publicly exposed network cameras, with support for specifying country and region.



![alt text](./pic/main.png)

---

# Video


<a href="https://www.youtube.com/watch?v=q4WR4QpiIwI">
  <img src="https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3Dq4WR4QpiIwI" width="32%">
</a>
<a href="https://www.youtube.com/watch?v=BaA30uFkXbc">
  <img src="https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DBaA30uFkXbc" width="32%">
</a>
<a href="https://www.youtube.com/watch?v=_HDXlHj8HlQ">
  <img src="https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D_HDXlHj8HlQ" width="32%">
</a>
 

---

# Install Dependencies

Disk space requirement: `Available space > 600 MB`

```bash
$ sudo apt update && sudo apt install ffmpeg python3-pyqt5.qtwebengine -y
$ git clone https://github.com/MartinxMax/BloodCat.git
$ cd BloodCat && python3 -m venv bloodcat
$ source ./bloodcat/bin/activate
(bloodcat)$ python -m pip install --upgrade pip
(bloodcat)$ pip install -r requirements.txt
``` 

If you are using the Windows operating system, please download `https://github.com/MartinxMax/BloodCat/releases/download/play/ffplay.exe` and move the downloaded .exe file into the `./lib/` directory.

---

# BloodCat Usage

```bash
(bloodcat)$ python3 bloodcat.py -h
```

![alt text](./pic/image.png)

---

## Bruteforce a specific camera IP

```bash
(bloodcat)$ python3 bloodcat.py --ip "188.134.80.244:554"
```

![alt text](./pic/image-1.png)

```bash
(bloodcat)$ python3 bloodcat_map.py
```

![alt text](./pic/image-3.png)

---

## Bruteforce for  IP list

```bash
(bloodcat)$ python3 bloodcat.py --ips target.txt
```

![alt text](./pic/image-4.png)

```bash
(bloodcat)$ python3 bloodcat_map.py
```


![alt text](./pic/image-5.png)


## Bruteforce camera IPs in a specific country/region (via FoFa)

```bash
(bloodcat)$ python3 bloodcat.py --country CN --region HK --key <FOFA-API-KEY>
```

![alt text](./pic/image-14.png)

---

## Merge .bc Data

Place all `.bc` files that need to be merged into the `./data/` directory.

![alt text](./pic/image-12.png)

```bash
(bloodcat)$ python3 bloodcat.py --merge
```


![alt text](./pic/image-13.png)

After execution,
`./data/20260108_171450.bc` will be a deduplicated and merged .bc file.

Replace the original global.bc file, then right-click Reload in BloodCat_Map:

```bash
(bloodcat)$ mv ./data/20260108_171450.bc ./data/global.bc
```

![alt text](./pic/image-15.png)

---

## Hikvision Crack && iVMS-4200

```bash
(bloodcat)$ python3 CVE-2017-7921_HIK_Auto_Crack.py --ips ./target.txt --json ./data/hik.json
```

![alt text](./pic/hik.png)


```bash
(bloodcat)$ python3 bloodcat.py --hiv ./data/hik.json
```

![alt text](./pic/hik2.png)


Download link : https://github.com/MartinxMax/BloodCat/releases/tag/play

```bash
(bloodcat)$ python3 CVE-2017-7921_HIK_Auto_Crack.py --ips ./target.txt --csv ./data/hik.csv
```

![alt text](./pic/hik3.png)

![alt text](./pic/hik4.png)

---

# Blood-Cat-Map Usage


```bash
(bloodcat)$ python3 bloodcat_map.py
```

 
![alt text](./pic/image-2.png)



## Remote API Data

By entering a remote data URL, you can load external datasets.

You may test using the official BloodCat database:

`https://raw.githubusercontent.com/MartinxMax/db/refs/heads/main/blood_cat/global.bc`

![alt text](./pic/image-6.png)


You can also copy API database links from other BloodCat-Map instances:

![alt text](./pic/image-10.png)

The target data will be loaded and displayed on the map.
If you need to remove an entry, click the X on the right side.
Remote-loaded raw data is not automatically saved locally,
but the remote URL will be written into the configuration file.

![alt text](./pic/image-11.png)

## IP Tracking


You can enter keywords here to perform fuzzy matching on targets.
This allows you to quickly lock and track specific targets on the map.

![alt text](./pic/image-7.png)

## Team Collaboration

To use the chat feature, all team members must:
· Be on the same local network (LAN)
· Run BloodCat-Map simultaneously

The good news is:
· No need to enter peer IP addresses
· No need to worry about sniffing attacks
· Chat packets are encrypted

TEAM A:
![alt text](./pic/image-8.png)
TEAM B:
![alt text](./pic/image-9.png)


---

