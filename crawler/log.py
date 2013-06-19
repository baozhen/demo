# -*- coding: utf-8 -*-
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='./licai.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)



def getLogging(name):
    return logging.getLogger(name)
