#!/usr/bin/env python3
import subprocess


def main():
    # failover test
    for i in range(50):
        # Run the command and print the output
        output = subprocess.check_output(["./send.py", "PUT", str(i), str(i)])
        print(output.decode("utf-8"))

    output = subprocess.check_output(["./send.py", "RANGE", "0", "50"])

if __name__ == "__main__":
    main()
