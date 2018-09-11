#!/usr/bin/env python3

"""
Download FireEye Carbanak report and save as CSV

"""

import io
import re
import argparse
import pyexcel_xlsx
import requests
import csv
import arrow
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def is_ip(addr):
    return re.search(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', addr)

def parseargs():
    """ Parse arguments """
    parser = argparse.ArgumentParser(description='Generate testdata from FireEye carbanak report')
    parser.add_argument("--logfile", dest="log_file", help="Log to file (default = stdout)")
    parser.add_argument("--loglevel", dest="log_level", default="info", help="Loglevel (default = info)")

    return parser.parse_args()

def get_xlsx_report(url, sheet_name):
    r = requests.get(url, verify=False)
    data = pyexcel_xlsx.get_data(io.BytesIO(r.content))
    return data[sheet_name]

def carbanak_report():
    with open('carbanak.csv', 'w', newline='') as csvfile:
        fieldnames = ['file_hash', 'dest_ip', 'domain', 'dest_port', 'protocol_version', 'compile_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in get_xlsx_report(
                "https://www.fireeye.com/content/dam/fireeye-www/blog/pdfs/carbanak-report.xlsx",
                "Sheet1")[1:]: # First row is header

            md5 = row[0]
            try:
                compile_time = arrow.get(row[1])
            except arrow.parser.ParserError:
                compile_time = None
            protocol_version = row[2]
            campaign = row[3]
            c2_list = row[4:]

            if not md5:
                continue

            if campaign and not campaign == "NA" and isinstance(campaign, str):
                pass
            else:
                campaign=None

            for c2 in c2_list:
                domain=None
                dest_ip=None
                dest_port=None

                c2_no_port = re.sub(r':.*$', "", c2)
                c2_port = re.sub(r'^[^:]*:', "", c2)

                if is_ip(c2_no_port):
                    dest_ip = c2_no_port
                else:
                    domain = c2_no_port

                if c2_port:
                    dest_port = c2_port

                row = {"file_hash": md5}
                if protocol_version:
                    row["protocol_version"] = protocol_version
                if compile_time:
                    row["compile_time"] = compile_time
                if dest_ip:
                    row["dest_ip"] = dest_ip
                if domain:
                    row["domain"] = domain
                if dest_port:
                    row["dest_port"] = dest_port

                writer.writerow(row)

if __name__ == '__main__':
    args = parseargs()
    carbanak_report()
