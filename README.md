# minitel-server
A small Minitel server written in Python.

## Introduction
This server serves Minitel pages located in pages folder.
A TCP socket (at port 3615) listens for connections. You can use this software with a Minitel emulator, like Hyperterm on Windows.
Or using Asterisk, to use a real Minitel hardware (and a real RTC phone line!) by using the softmodem module.
A Docker image is available on my Github to ease the usage of Asterisk.

## Bug
Probably a lot.

## Thanks
Thanks to Christian Quest for sharing [Pynitel](https://github.com/cquest/pynitel).
It helps me a lot!