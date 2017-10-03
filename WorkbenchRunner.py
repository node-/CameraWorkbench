#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author: Jacob Kosberg
"""

import CameraWorkbench
import time
import emailer

def failed():
    subject = "Experiment Update"
    body = "Something went wrong."
    emailer.emailScreenshot(subject, body)


def main():
    while True:
        CameraWorkbench.main()
        failed()

if __name__ == "__main__":
    main()