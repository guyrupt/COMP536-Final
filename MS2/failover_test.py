#!/usr/bin/env python3
import subprocess


def main():
    for i in range(100):
        # Run the command and print the output
        output = subprocess.check_output(["./send.py", "PUT", str(i), str(i)])
        print(output.decode("utf-8"))


if __name__ == "__main__":
    main()
