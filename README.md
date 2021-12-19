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
    You should see a vareity of files that were cloned from the remote GitHub repository:
    ```
    pi@raspberrypi:~ $ ls -la ~/Documents/Pi-kalman/
    total 40
    drwxr-xr-x 4 pi pi 4096 Dec 18 14:43 .
    drwxr-xr-x 3 pi pi 4096 Dec 18 14:42 ..
    drwxr-xr-x 8 pi pi 4096 Dec 18 15:03 .git
    -rw-r--r-- 1 pi pi   66 Dec 18 14:43 .gitattributes
    -rw-r--r-- 1 pi pi    7 Dec 18 14:43 .gitignore
    drwxr-xr-x 3 pi pi 4096 Dec 18 14:43 .idea
    -rw-r--r-- 1 pi pi 5607 Dec 18 15:03 kalman.py
    -rw-r--r-- 1 pi pi  610 Dec 18 14:43 README.md
    -rw-r--r-- 1 pi pi    5 Dec 18 14:43 requirements.txt
    ...
    ```
    Most importantly, we can now access some important files that we will use later on:
    ```bash
    cat ~/Documents/Pi-kalman/kalman.py
    ```
    ```
    """Pi-kalman"""

    import numpy as np


    class KalmanFilter(object):
    ...
    ```

## Setting up Skyhook on the Raspberry Pi
[skyhook](https://www.skyhook.com/devices/raspberry_pi_cartracker_location_tutorial)

[github](https://github.com/SkyhookWireless/skyhook-location-native/wiki/Raspberry-Pi-Offline-Tracker?__hstc=213337803.5c7ba8d8a7f1e56792af19d74e1f3e03.1630335901094.1630335901094.1630355890466.2&__hssc=213337803.2.3262525312423263e%2B23.1630355890466&__hsfp=2763330627&hsCtaTracking=fa0eb42e-8d8e-46e3-a96a-24edc6696059%7C3d8ff17d-883d-42c3-8721-83d523138e2c
)

## Kalman Filter Background
Kalman filter [python implementation](https://arxiv.org/pdf/1204.0375.pdf)