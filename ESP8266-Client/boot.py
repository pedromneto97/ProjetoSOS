from esp import osdebug
from machine import freq
from gc import collect

freq(160000000)
osdebug(None)
collect()