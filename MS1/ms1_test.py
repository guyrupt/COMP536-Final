#!/usr/bin/env python3
import subprocess


def main():
    # Put test
    output = subprocess.check_output(["./send.py", "PUT", "1", "1"])
    print("PUT 1 1")

    # Get test
    output = subprocess.check_output(["./send.py", "GET", "1", "0"])
    print("GET 1 0")

    # Get null value
    output = subprocess.check_output(["./send.py", "GET", "2", "0"])
    print("GET 2 0")

    # Put multiple values for range test
    for i in range(10):
        output = subprocess.check_output(["./send.py", "PUT", str(i), str(i)])
    print("PUT 0-9 0-9")

    # Range test
    output = subprocess.check_output(["./send.py", "RANGE", "0", "9", "0"])

    # Select test
    output = subprocess.check_output(["./send.py", "SELECT", "<", "10", "0"])

    # Versioning test
    output = subprocess.check_output(["./send.py", "PUT", "100", "0"])
    output = subprocess.check_output(["./send.py", "PUT", "100", "1"])
    output = subprocess.check_output(["./send.py", "PUT", "100", "2"])

    output = subprocess.check_output(["./send.py", "GET", "100", "0"])
    output = subprocess.check_output(["./send.py", "GET", "100", "1"])
    output = subprocess.check_output(["./send.py", "GET", "100", "2"])


if __name__ == "__main__":
    main()
