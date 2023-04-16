#!/usr/bin/env python3
import subprocess


def main():
    # Testing with Alice

    # Put test
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "1", "1"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")

    # Get test
    send_process = subprocess.Popen(
        ["./send.py", "GET", "1", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")

    # Get test. Should get null value but still has read access
    send_process = subprocess.Popen(
        ["./send.py", "GET", "555", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")

    # Put test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "555", "1"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")

    # Range test on valid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "0", "9", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")

    # Range test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "555", "560", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")

    # Testing with Bob

    # Put test
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "1", "1"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")

    # Get test
    send_process = subprocess.Popen(
        ["./send.py", "GET", "1", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")

    # Get test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "GET", "300", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")

    # Put test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "300", "1"], stdin=subprocess.PIPE
    )

    # Range test on valid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "0", "9", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")

    # Range test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "250", "260", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")


if __name__ == "__main__":
    main()
