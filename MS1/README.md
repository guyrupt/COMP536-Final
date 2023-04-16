# Milestone 1

## Files Created

```
├── README.md
├── Makefile
├── ms1.p4          # P4 implementation of KVS
├── s1-runtime.json # runtime config for switch s1
├── topology.json   # topology file
├── send.py         # Script to send packets
├── receive.py      # Script to receive packets
```

## Testing

1. Compile and enter mininet environment

    ```bash
    make 
    ```
   If you want to clean the environment, run `make clean` first.

    Then, in mininet CLI, run `xterm` to open two terminals for `h1`
        
    ```
    mininet> xterm h1 h1
    ```

2. Run `receive.py` in one terminal

    ```bash
    ./receive.py
    ```

3. Run `send.py` in another terminal

    ```bash
    ./send.py <operation> <options>
    ```

    Here are the supported operations:

    - `GET <key> <version>`
    - `PUT <key> <value>`
    - `RANGE <key1> <key2> <version>`
    - `SELECT <operand> <value> <version> `
