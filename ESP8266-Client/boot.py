#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is executed on every boot (including wake-boot from deepsleep)
import esp
from machine import freq
from gc import collect
from webrepl import start

freq(160000000)
esp.osdebug(None)
start()
collect()