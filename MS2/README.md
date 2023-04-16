# Milestone 2

## Files Created

```
├── README.md
├── Makefile
├── s0.p4           # Load balancer
├── s1.p4           # KVS implementation, shard 1
├── s2.p4           # KVS implementation, shard 2
├── s3.p4           # KVS backup implementation
├── pod-topo/       # topology file & runtime configs for each switch
│   ├── s0-runtime.json  
│   ├── s1-runtime.json
│   ├── s2-runtime.json
│   ├── s3-runtime.json
│   ├── topology.json
├── send.py             # Script to send packets
├── receive.py          # Script to receive packets
├── ms3_test.py         # Testing script
├── failover_test.py    # Failover testing script
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

    - `GET <key>`
    - `PUT <key> <value>`
    - `RANGE <key1> <key2>`
    - `SELECT <operand> <value> `


## Testing Script and Intended Output

### Load Balace Test
[ms2_test.py](./ms2_test.py) is a pre-written testing script. Make sure the network is at clean start before running the script. For the testing details, please refer to the actual script.

To run, instead of running `send.py` in step 3, run

```bash
./ms2_test.py
```

You should see the following output in the terminal running `receive.py`:

```
sniffing on eth0
[Switch 1] inserted
[Switch 1] value: 512
[Switch 2] value is null
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
[Switch 1] inserted
range query
[Switch 1] value: 0
[Switch 1] value: 1
[Switch 1] value: 2
[Switch 1] value: 3
[Switch 1] value: 4
[Switch 1] value: 5
[Switch 1] value: 6
[Switch 1] value: 7
[Switch 1] value: 8
[Switch 1] value: 9
range query
[Switch 1] value: 0
[Switch 1] value: 1
[Switch 1] value: 2
[Switch 1] value: 3
[Switch 1] value: 4
[Switch 1] value: 5
[Switch 1] value: 6
[Switch 1] value: 7
[Switch 1] value: 8
[Switch 1] value: 9
range query
[Switch 1] value is null
[Switch 1] value is null
[Switch 1] value is null
[Switch 1] value is null
[Switch 1] value is null
[Switch 1] inserted
[Switch 2] inserted
[Switch 2] inserted
[Switch 1] value: 0
range query
[Switch 2] value: 1
[Switch 2] value: 2
```
### Failover Test
[failover_test.py](./failover_test.py) is a pre-written testing script. This failover test tests the ability of KVS to restore values after switch 1 is down. Specifically, after sending 40 packets, there are total of 5 ping packets unanswered. Therefore, after the switch finds out # of unanswered packets >= 5 at 45 seconds, it will redirect traffics to switch 3.


To run, add the following line in step 1
```
mininet> link s0 s1 down
```
Then, instead of running `send.py` in step 3, run

```bash
./failover_test.py
```

You should see the following output in the terminal running `receive.py`:

```
sniffing on eth0
[Switch 3] inserted
[Switch 3] inserted
[Switch 3] inserted
[Switch 3] inserted
[Switch 3] inserted
range query
[Switch 3] value: 0
[Switch 3] value: 1
[Switch 3] value: 2
[Switch 3] value: 3
[Switch 3] value: 4
[Switch 3] value: 5
[Switch 3] value: 6
[Switch 3] value: 7
[Switch 3] value: 8
[Switch 3] value: 9
range query
[Switch 3] value: 10
[Switch 3] value: 11
[Switch 3] value: 12
[Switch 3] value: 13
[Switch 3] value: 14
[Switch 3] value: 15
[Switch 3] value: 16
[Switch 3] value: 17
[Switch 3] value: 18
[Switch 3] value: 19
range query
[Switch 3] value: 20
[Switch 3] value: 21
[Switch 3] value: 22
[Switch 3] value: 23
[Switch 3] value: 24
[Switch 3] value: 25
[Switch 3] value: 26
[Switch 3] value: 27
[Switch 3] value: 28
[Switch 3] value: 29
range query
[Switch 3] value: 30
[Switch 3] value: 31
[Switch 3] value: 32
[Switch 3] value: 33
[Switch 3] value: 34
[Switch 3] value: 35
[Switch 3] value: 36
[Switch 3] value: 37
[Switch 3] value: 38
[Switch 3] value: 39
range query
[Switch 3] value: 40
[Switch 3] value: 41
[Switch 3] value: 42
[Switch 3] value: 43
[Switch 3] value: 44
[Switch 3] value: 45
[Switch 3] value: 46
[Switch 3] value: 47
[Switch 3] value: 48
[Switch 3] value: 49
range query
[Switch 3] value is null
```


