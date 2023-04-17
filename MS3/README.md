# Milestone 3

## Files Created

```
├── README.md
├── Makefile
├── s0.p4           # Load balancer & ACL implementation
├── s1.p4           # KVS implementation, shard 1
├── s2.p4           # KVS implementation, shard 2
├── s3.p4           # KVS backup implementation
├── pod-topo/       # topology file & runtime configs for each switch
│   ├── s0-runtime.json  
│   ├── s1-runtime.json
│   ├── s2-runtime.json
│   ├── s3-runtime.json
│   ├── topology.json
├── send.py         # Script to send packets
├── receive.py      # Script to receive packets
├── ms3_test.py     # Testing script
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

    After the command, user will be prompt `Sending request as: (0) Alice (1) Bob`. Enter `0` or `1` to choose the client.

## Testing Script and Intended Output

[ms3_test.py](./ms3_test.py) is a pre-written testing script. Make sure the network is at clean start before running the script. For the testing details, please refer to the actual script.

To run, instead of running `send.py` in step 3, run

```bash
./ms3_test.py
```

You should see the following output in the terminal running `receive.py`:

```
sniffing on eth0
inserted 
value: 1 
value is null
write unauthorized
range query 
value is null 
value: 1 
value is null 
value is null 
value is null 
value is null 
value is null 
value is null 
value is null 
value is null 
range query 
value is null 
value is null 
value is null 
value is null 
value is null 
value is null 
inserted 
value: 1
read and write unauthorized for some of the keys
read and write unauthorized for some of the keys
range query 
value is null 
value: 1 
value is null 
value is null 
value is null 
value is null 
value is null 
value is null 
value is null 
value is null
read and write unauthorized for some of the keys
```

