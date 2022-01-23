#!/usr/bin/env python3
# OSINT/Infrastructure/check_live.py

# check_live.py
#   Check if a supplied list of Domains are live (HTTP 200)


# Imports
import argparse
import signal
import requests


def ctrl_c(sig, frame):
    print("\n{} chose to quit via CTRL+C!".format(os.environ['USER']))
    sys.exit(0)


def parse_file(filepath):
    
    domains = []

    with open(filepath) as fp:
        line = fp.readline()
        while line:
            domains.append(line.strip())
            line = fp.readline()

    return domains


def check_live(domains):

    count = 0
    
    for domain in domains:
        try:
            if "*" in domain:
                continue
            if requests.get("https://{}".format(domain)).status_code == 200:
                print("{}".format(domain))
                count += 1
        except Exception:
            continue
    
    if count == 0:
        print("None")


def main():

    parser = argparse.ArgumentParser(description="Check if domain is live (HTTP 200)")
    parser.add_argument("-f", "--file", action='store', dest='filepath', required=True,  
                        help="File containing domains to check")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, ctrl_c)
    
    domains_to_check = parse_file(args.filepath)
    check_live(domains_to_check)

    exit(0)


if __name__== "__main__":
    main()

