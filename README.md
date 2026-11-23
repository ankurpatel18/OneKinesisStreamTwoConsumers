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

## Troubleshooting

If Python reports that it cannot open lab.py, run `pwd` and `ls` (PowerShell: `Get-Location` and `dir`) and switch to the folder containing the extracted script. If the Python command is unavailable, install Python 3 and reopen the terminal. Run with assertions enabled, using the command above.
