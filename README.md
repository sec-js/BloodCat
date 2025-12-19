 

# Blood-Cat

A tool for hacking into publicly exposed network cameras, with support for specifying country and region

```
Version 1.3
[+] Added a log output interface for a more elegant output display. 
[+] Added the --ips parameter to support importing multiple IP lists; in domain penetration, BloodCat can help you compromise more cameras.
```

![alt text](./pic/TEST-2.png)

![alt text](./pic/TEST-1.png)



![alt text](./pic/TEST-3.png)


---

# Install Dependencies

```bash
$ sudo apt update && sudo apt install ffmpeg
$ pip install tqdm requests
```

---

# Usage

```bash
$ python3 bloodcat.py -h
```

![alt text](./pic/image.png)

---

## Bruteforce for  IP list

```bash
$ python3 bloodcat.py --ips target.txt
```

![alt text](./pic/TEST-1.png)

## Bruteforce a specific camera IP

```bash
$ python3 bloodcat.py --ip "80.191.192.230:554"
```

![alt text](./pic/image-1.png)
![alt text](./pic/image-5.png)

---

## Bruteforce camera IPs in a specific country/region (via FoFa)

```bash
$ python3 bloodcat.py --country CN --region HK --key <FOFA-API-KEY>
```

![alt text](./pic/image-2.png)

---

# File Path

All discovered results will be saved to:

```
./data/ipcam.info
```

![alt text](./pic/image-3.png)

---

# Launch Viewer

```bash
$ ./play.sh
```

![alt text](./pic/image-4.png)


 
