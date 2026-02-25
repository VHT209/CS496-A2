# Analysis: Quorum vs Gossip Performance

> **Instructions:** Copy this template to your submission as `ANALYSIS.md` and fill in all sections.
> Replace all `[bracketed text]` with your actual observations and measurements.
>
> **Tip:** Use the benchmark tool to automate measurements:
> ```bash
> python3 benchmark_tool.py --mode quorum   # While cluster runs in Quorum mode
> python3 benchmark_tool.py --mode gossip   # While cluster runs in Gossip mode
> ```
> The tool outputs results in a format you can paste directly into Section 2.

## 1. Test Environment
- **OS:** [e.g., Windows 11 / macOS 14 / Ubuntu 22.04]
- **Docker Version:** [output of `docker --version`]
- **Python Version:** [output of `python3 --version`]

## 2. Response Time Comparison

> Run `python3 benchmark_tool.py --mode quorum` and `python3 benchmark_tool.py --mode gossip` 
> to collect these measurements automatically.

### Quorum Mode (Strong Consistency)
| Test | Response Time (ms) | Status Code |
|------|-------------------|-------------|
| Single message POST | [e.g., 45] | 200 |
| 5 concurrent POSTs (avg) | [e.g., 78] | 200 |

### Gossip Mode (Eventual Consistency)
| Test | Response Time (ms) | Status Code |
|------|-------------------|-------------|
| Single message POST | [e.g., 12] | 202 |
| 5 concurrent POSTs (avg) | [e.g., 15] | 202 |

## 3. Convergence Test (Gossip Mode)
- **Time for message to appear on all nodes:** [e.g., 4.2 seconds]
- **Number of gossip rounds observed:** [e.g., 2]

## 4. Partition Test

Test the same scenario in BOTH modes to observe the CAP trade-off:

### Scenario: Kill 2 of 3 nodes, then attempt a write

| Mode | Command | Status Code | Behavior |
|------|---------|-------------|----------|
| Quorum (STRONG) | `curl -X POST localhost:5001/message ...` | [e.g., 500] | [Describe] |
| Gossip (EVENTUAL) | `curl -X POST localhost:5001/message ...` | [e.g., 202] | [Describe] |

### Observations
- **Quorum behavior during partition:** [Did it reject the request? Why?]
- **Gossip behavior during partition:** [Did it accept the request? What are the risks?]

## 5. CAP Theorem Analysis

### Which CAP properties does each mode prioritize?
| Mode | CAP Choice | Explanation |
|------|------------|-------------|
| Quorum | [CP / AP / CA] | [Why? What does it sacrifice?] |
| Gossip | [CP / AP / CA] | [Why? What does it sacrifice?] |

### Why can't we have all three (CAP)?
[Your explanation - What makes it impossible to guarantee C, A, and P simultaneously?]

### Real-World Trade-off Scenarios
Answer: Which mode would you choose for each scenario, and why?

1. **Bank account balance:** [Quorum/Gossip] because [reason]
Quorum, because we need a high consistency and we can tolerate a bit of unavailability. It would be bad if the bank account balance is different in two locations. 
2. **Social media "likes" counter:** [Quorum/Gossip] because [reason]
Gossip, because we want  
3. **Airline seat reservation:** [Quorum/Gossip] because [reason]
4. **User online/offline status:** [Quorum/Gossip] because [reason]

## 6. Performance Observations

### Why is Quorum slower?
[Your explanation - e.g., "Quorum must wait for network round-trips to 2 other nodes before responding..."]

### Why is Gossip faster but temporarily inconsistent?
[Your explanation - e.g., "Gossip returns immediately after local write. The propagation delay means..."]

## 7. Testing Commands Used
```bash
# Example commands you ran
curl -X POST http://localhost:5001/message -H "Content-Type: application/json" -d '{"text":"test","user":"alice"}'
curl http://localhost:5002/messages
```


============================================================
BENCHMARK: QUORUM MODE
Timestamp: 2026-02-24T12:51:13.142020
============================================================

Checking cluster health...
  http://localhost:5001: OK
  http://localhost:5002: OK
  http://localhost:5003: OK

[1/3] Sequential POST Benchmark
  Running 10 sequential POST requests to http://localhost:5001...
    [1/10] 9.62ms - OK
    [2/10] 7.10ms - OK
    [3/10] 7.84ms - OK
    [4/10] 6.75ms - OK
    [5/10] 7.47ms - OK
    [6/10] 7.00ms - OK
    [7/10] 7.15ms - OK
    [8/10] 7.52ms - OK
    [9/10] 6.84ms - OK
    [10/10] 7.16ms - OK

  Sequential Results:
    Requests: 10/10 successful
    Min:      6.75 ms
    Max:      9.62 ms
    Mean:     7.45 ms
    Median:   7.16 ms
    Std Dev:  0.83 ms

[2/3] Concurrent POST Benchmark
  Running 5 concurrent POST requests to http://localhost:5001...
    Total time for 5 concurrent requests: 36.96ms

  Concurrent Results:
    Requests: 5/5 successful
    Min:      27.54 ms
    Max:      36.10 ms
    Mean:     31.91 ms
    Median:   32.46 ms
    Std Dev:  3.45 ms

[3/3] Convergence Test
  Running convergence test...
    POST response time: 7.49 ms
    http://localhost:5002: converged in 9.87 ms
    http://localhost:5003: converged in 12.03 ms

============================================================
COPY THE FOLLOWING INTO YOUR ANALYSIS.md:
============================================================

### Quorum Mode (Strong Consistency)
| Test | Response Time (ms) | Status Code |
|------|-------------------|-------------|
| Single message POST | 7.45 | 200 |
| GET /messages | [measure manually] | 200 |
| 5 concurrent POSTs (avg) | 31.91 | 200 |

**Convergence Time:** Immediate (synchronous replication)

============================================================


============================================================
BENCHMARK: GOSSIP MODE
Timestamp: 2026-02-24T12:52:53.991074
============================================================

Checking cluster health...
  http://localhost:5001: OK
  http://localhost:5002: OK
  http://localhost:5003: OK

[1/3] Sequential POST Benchmark
  Running 10 sequential POST requests to http://localhost:5001...
    [1/10] 2.09ms - OK
    [2/10] 2.21ms - OK
    [3/10] 2.37ms - OK
    [4/10] 2.67ms - OK
    [5/10] 2.07ms - OK
    [6/10] 1.92ms - OK
    [7/10] 2.03ms - OK
    [8/10] 2.61ms - OK
    [9/10] 2.28ms - OK
    [10/10] 2.53ms - OK

  Sequential Results:
    Requests: 10/10 successful
    Min:      1.92 ms
    Max:      2.67 ms
    Mean:     2.28 ms
    Median:   2.24 ms
    Std Dev:  0.26 ms

[2/3] Concurrent POST Benchmark
  Running 5 concurrent POST requests to http://localhost:5001...
    Total time for 5 concurrent requests: 11.47ms

  Concurrent Results:
    Requests: 5/5 successful
    Min:      5.95 ms
    Max:      8.36 ms
    Mean:     7.14 ms
    Median:   6.56 ms
    Std Dev:  1.12 ms

[3/3] Convergence Test
  Running convergence test...
    POST response time: 3.07 ms
    http://localhost:5002: converged in 5533.68 ms
    http://localhost:5003: converged in 5535.52 ms

============================================================
COPY THE FOLLOWING INTO YOUR ANALYSIS.md:
============================================================

### Gossip Mode (Eventual Consistency)
| Test | Response Time (ms) | Status Code |
|------|-------------------|-------------|
| Single message POST | 2.28 | 202 |
| GET /messages | [measure manually] | 200 |
| 5 concurrent POSTs (avg) | 7.14 | 202 |

**Convergence Time:** 5535.52 ms for all nodes

============================================================