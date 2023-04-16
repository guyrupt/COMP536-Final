#!/usr/bin/env python3
import subprocess


def main():
    # Put test
    output = subprocess.check_output(["./send.py", "PUT", "512", "512"])
    print("PUT 512 512")

    # Get test
    output = subprocess.check_output(["./send.py", "GET", "512"])
    print("GET 512")

    # Get null value
    output = subprocess.check_output(["./send.py", "GET", "1024"])
    print("GET 1024")

    # Put multiple values for range test
    for i in range(10):
        output = subprocess.check_output(["./send.py", "PUT", str(i), str(i)])
    print("PUT 0-9 0-9")

    # Range test
    output = subprocess.check_output(["./send.py", "RANGE", "0", "9"])
    print("RANGE 0-9")

    # Select test
    output = subprocess.check_output(["./send.py", "SELECT", "<", "15"])
    print("SELECT < 15")

    # Load balance test
    output = subprocess.check_output(["./send.py", "PUT", "512", "0"])
    output = subprocess.check_output(["./send.py", "PUT", "513", "1"])
    output = subprocess.check_output(["./send.py", "PUT", "514", "2"])

    output = subprocess.check_output(["./send.py", "GET", "512"])
    output = subprocess.check_output(["./send.py", "RANGE", "513", "514"])


if __name__ == "__main__":
    main()
