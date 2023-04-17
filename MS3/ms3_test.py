#!/usr/bin/env python3
import subprocess


def main():
    # Testing with Alice

    # Put test
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "1", "1"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Get test
    send_process = subprocess.Popen(
        ["./send.py", "GET", "1", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Get test. Should get null value but still has read access
    send_process = subprocess.Popen(
        ["./send.py", "GET", "555", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Put test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "555", "1"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Range test on valid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "0", "9", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Range test on another valid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "555", "560", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"0")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Testing with Bob

    # Put test
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "1", "1"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Get test
    send_process = subprocess.Popen(
        ["./send.py", "GET", "1", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Get test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "GET", "300", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Put test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "PUT", "300", "1"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Range test on valid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "0", "9", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass

    # Range test on invalid range
    send_process = subprocess.Popen(
        ["./send.py", "RANGE", "251", "260", "0"], stdin=subprocess.PIPE
    )
    send_process.stdin.write(b"1")
    send_process.stdin.close()

    # Wait for the process to finish
    while send_process.poll() is None:
        pass


if __name__ == "__main__":
    main()
