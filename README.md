# Kinesis two-consumer lab

Follow one order through a shard reader and a queue worker pool. This Python simulation uses a logical clock to demonstrate a crash after a write, an expired visibility window, and a dead-letter restore.

## Run and verify

1. **Extract the ZIP.** Open the extracted folder and find `lab.py` beside `README.md`. Open a terminal in that folder.
2. **Check Python.** Run `python3 --version` on macOS or Linux, or `py -3 --version` on Windows. Use Python 3.8 or later. The lab uses only the standard library and runs offline.
3. **Run the lab.** Enter `python3 lab.py` (Windows: `py -3 lab.py`). One command runs all three fault scenarios and prints the worker trace. Each run starts with an empty in-memory ledger.
4. **Check ordering and retries.** The first line shows the shard reader advancing from accepted to packed to shipped. Find e2 at t=00 and t=05. The first worker inserts its row. The retry reports `existing ledger row`. For e1, the first worker pauses before writing, so its retry inserts the row.
5. **Verify recovery.** At t=17, e3 enters dead-letter state. At t=18, after the handler gains support for its template, a worker receives e3 again. Confirm the final line matches the one below.

```text
PASS: ordered projection, three unique rows, seven delivery attempts
```

## Observed lab outcomes

The dashboard reached **shipped** while the receipt for that same event still needed repair. Its history followed versions 1, 2, and 3. The workers first wrote receipts in a different order: **packed**, **accepted**, then **shipped**.

| Event and fault | Worker trace (logical ticks) | Durable outcome |
|---|---|---|
| e1 · accepted · pause before write | B paused at tick 1. A retried at tick 6 after visibility expired. | Two receives, one insert. The retry performed the missing work. |
| e2 · packed · crash after write | A inserted at tick 0. B found the existing row at tick 5. | Two receives, one insert. The stable key prevented a second receipt. |
| e3 · shipped · unsupported template | Workers received e3 at ticks 2, 7, and 12. It entered dead-letter state at 17. After repair and restore, A inserted at 18. | Four receives across the original and restored deliveries, one insert. |

**Final reconciliation:** 3 source events, 7 queue receives, 3 unique receipt rows, and all 3 events acknowledged. The counts and ticks come from the deterministic local simulation. They provide a correctness check for this fixture, not a measurement of AWS latency or throughput.

## Troubleshooting

If Python reports that it cannot open lab.py, run `pwd` and `ls` (PowerShell: `Get-Location` and `dir`) and switch to the folder containing the extracted script. If the Python command is unavailable, install Python 3 and reopen the terminal. Run with assertions enabled, using the command above.
