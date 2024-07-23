#!/usr/bin/env python

import csv
import json
from crud import read

def split_words(s):
    s.replace(",", " ")
    s.replace("_", " ")
    s.replace(";", " ")
    s = s.split()
    return s