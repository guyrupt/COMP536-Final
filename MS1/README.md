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
├── ms1_test.py     # Testing script
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

## Testing Script and Intended Output

[ms1_test.py](./ms1_test.py) is a pre-written testing script. Make sure the network is at clean start before running the script. For the testing details, please refer to the actual script. 

To run, instead of running `send.py` in step 3, run

```bash
./ms1_test.py
```

You should see the following output in the terminal running `receive.py`:

```
sniffing on eth0 
inserted 
value: 1 
value is null 
inserted
inserted
inserted
inserted
inserted
inserted
inserted
inserted
inserted
inserted 
range query 
value: 0
value: 1
value: 2 
value: 3 
value: 4
value: 5
value: 6 
value: 7
value: 8
value: 9 
range query 
value: 0
value: 1
value: 2 
value: 3
value: 4
value: 5
value: 6
value: 7
value: 8
value: 9 
inserted 
inserted 
inserted 
value: 0
value: 1
value: 2

```
