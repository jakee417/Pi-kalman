# Pi-kalman
 A fun [Global Positioning System (GPS) -tracking application](https://en.wikipedia.org/wiki/GPS_tracking_unit) that uses a [live GPS stream](https://www.skyhook.com/devices/raspberry_pi_cartracker_location_tutorial) and the [kalman filter](https://en.wikipedia.org/wiki/Kalman_filter) to track, log, and denoise GPS observations on a [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi).


 The specific model of Raspberry Pi that was used in making this tutorial is: [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)

## General Setup of the Raspberry-Pi
- Install the operating system (OS). Follow the provided manufactor's instructions ([CanaKit](https://www.canakit.com/raspberry-pi-zero-2-w.html) in my case). After installation, ensure that you have an internet connection.
    ```bash
    pi@raspberrypi:~ $ ping www.google.com
    PING www.google.com(nuq04s44-in-x04.1e100.net (2607:f8b0:4005:802::2004)) 56 data bytes
    64 bytes from sfo07s26-in-x04.1e100.net (2607:f8b0:4005:802::2004): icmp_seq=1 ttl=117 time=14.6 ms
    ...
    ```
- Setup [Secure Shell](https://en.wikipedia.org/wiki/Secure_Shell) (ssh). This is how we will remotely access the Raspberry Pi from a different computer. Follow [these steps](https://www.raspberrypi.com/documentation/computers/remote-access.html#ssh) to setup ssh on the Raspberry Pi. 

- You can then connect to the Rasperry Pi from another computer by following [these steps](https://en.wikipedia.org/wiki/Raspberry_Pi). You should have the ability to do this (assuming default user/host names):
    ```bash
    ssh pi@raspberrypi.local
    ```
    And see this output after answering a couple yes/no questions:
    ```
    Linux raspberrypi 5.10.63-v7+ #1459 SMP Wed Oct 6 16:41:10 BST 2021 armv7l

    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.

    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Sat Dec 18 14:52:59 2021 from 2601:646:8302:38d0:3c33:e145:631d:c161
    pi@raspberrypi:~ $ 
    ```
    Now we can run shell commands that control our Raspberry Pi remotely!

## Setup Github on Raspberry-Pi
- [setup ssh and link to GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/about-ssh). You should be able to replicate this:
    ```
    pi@raspberrypi:~/.ssh $ ls -la  ~/.ssh
    total 24
    drwx------  2 pi pi 4096 Dec 18 14:42 .
    drwxr-xr-x 16 pi pi 4096 Dec 18 15:50 ..
    -rw-r--r--  1 pi pi   61 Dec 18 14:38 config
    -rw-------  1 pi pi  464 Dec 18 14:41 id_ed25519
    -rw-r--r--  1 pi pi  106 Dec 18 14:33 id_ed25519.pub
    -rw-r--r--  1 pi pi  666 Dec 18 14:30 known_hosts```
- Clone the `Pi-kalman` respository with:
    ```bash
    cd ~/Documents
    git clone git@github.com:jakee417/Pi-kalman.git
    ```
    We can verify the files have appeared by viewing the contents of the `~/Documents/Pi-kalman` directory:
    ```bash
    la -la ~/Documents/Pi-kalman
    ```
    You should see a variety of files that were cloned from the remote GitHub repository. Most importantly, we can now access some important files that we will use later on:
    ```bash
    cat ~/Documents/Pi-kalman/gps_tracker.py
    ```
    ```
    """Pi-kalman"""

    import numpy as np


    class KalmanFilter(object):
    ...
    ```

## Setting up Python on Raspberry Pi
### Python
Two versions of Python come built-in with Raspberry Pi. We can easily see them using the `python` and `python3` alias commands:
```
pi@raspberrypi:~ $ python --version
Python 2.7.18
```

```
pi@raspberrypi:~ $ python3 --version
Python 3.9.2
```
For our purposes, `Python 3.9.2` will work just fine. 
### Python Libraries
We will need additional libraries, specifically:
```bash
pi@raspberrypi:~/Documents/Pi-kalman $ cat ~/Documents/Pi-kalman/requirements.txt
numpy
```
For `numpy` to work on the `Raspberry Pi`, [we need one additional library](https://stackoverflow.com/questions/53347759/importerror-libcblas-so-3-cannot-open-shared-object-file-no-such-file-or-dire):
```bash
sudo apt-get install libatlas-base-dev
```

### [Virtual Environment](https://docs.python.org/3/tutorial/venv.html)
We can finish our installs inside a `Virtual Environment` which you can think of as a standalone copy of Python that is isolated from both of the base installations (`Python 2.7.18` and `Python 3.9.2`). We will use this version of `Virtual Environment`:
```bash
sudo apt install virtualenv python3-virtualenv -y
```
The advantage to this is that if we break our `Virtual Environment`, then we can simply delete the `Virtual Environment` files and not corrupt our default builds.
Create a `Virtual Environment` using:
```bash
cd ~/Documents/Pi-kalman/
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
```
Now the command line should appear as:
```
(venv) pi@raspberrypi:~/Documents/Pi-kalman $
```
Where `(venv)` appears as a prefix to our username. We can verify the python files and libraries with:
```bash
(venv) pi@raspberrypi:~/Documents/Pi-kalman $ ls venv/bin
activate  activate.csh  activate.fish  Activate.ps1  easy_install  easy_install-3.9  f2py  f2py3  f2py3.9  pip  pip3  pip3.9  python  python3  python3.9
(venv) pi@raspberrypi:~/Documents/Pi-kalman $ which python
/home/pi/Documents/Pi-kalman/venv/bin/python
(venv) pi@raspberrypi:~/Documents/Pi-kalman $ pip freeze
(venv) pi@raspberrypi:~/Documents/Pi-kalman $ 
```
Which shows we are using `/home/pi/Documents/Pi-kalman/venv/bin/python` which is the `venv`'s `bin` folder and that the libraries installed are empty currently.
Finally, install `numpy` on `venv` with:
```bash
pip install numpy -v
```
You should see [`"https://www.piwheels.org/simple/numpy/numpy-1.21.5-cp39-cp39-linux_armv7l.whl"`](https://www.piwheels.org/) mentioned somewhere in the output which tells us we are using the Raspberry-Pi specific pypi server. Then we verify
```bash
(venv) pi@raspberrypi:~/Documents/Pi-kalman $ pip freeze
numpy==1.21.5
```
## Setting up Skyhook on the Raspberry Pi
[skyhook](https://www.skyhook.com/devices/raspberry_pi_cartracker_location_tutorial)

[github](https://github.com/SkyhookWireless/skyhook-location-native/wiki/Raspberry-Pi-Offline-Tracker?__hstc=213337803.5c7ba8d8a7f1e56792af19d74e1f3e03.1630335901094.1630335901094.1630355890466.2&__hssc=213337803.2.3262525312423263e%2B23.1630355890466&__hsfp=2763330627&hsCtaTracking=fa0eb42e-8d8e-46e3-a96a-24edc6696059%7C3d8ff17d-883d-42c3-8721-83d523138e2c
)

## Kalman Filter Background
Kalman filter [python implementation](https://arxiv.org/pdf/1204.0375.pdf)