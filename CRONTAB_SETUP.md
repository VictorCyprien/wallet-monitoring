# Setting Up Automated Execution with Crontab

This guide explains how to set up a crontab job to run the wallet monitor script every 2 hours.

## Verify the Script

First, make sure the `run_wallet_monitor.sh` script works correctly:

```bash
./run_wallet_monitor.sh
```

## Setting Up the Crontab

1. Open your crontab configuration:

```bash
crontab -e
```

2. Add the following line to run the script every 2 hours:

```
0 */2 * * * /full/path/to/your/run_wallet_monitor.sh >> /full/path/to/your/cron_output.log 2>&1
```

Replace `/full/path/to/your/` with the actual full path to your project directory.

3. Save and exit the editor.

## Understanding the Cron Schedule

The schedule format is: `minute hour day-of-month month day-of-week command`

- `0` - Run at minute 0 (at the top of the hour)
- `*/2` - Run every 2 hours
- `* * *` - Run on all days of the month, all months, and all days of the week

## Verifying Crontab Setup

To verify your crontab is set up correctly:

```bash
crontab -l
```

## Troubleshooting

If the cron job isn't running as expected:

1. Check the cron log:
```bash
grep CRON /var/log/syslog
```

2. Ensure your script has proper permissions:
```bash
chmod +x run_wallet_monitor.sh
```

3. Try using absolute paths for all commands in the script

4. Check the cron_output.log file for errors

## Alternative: Running Every 2 Hours Starting at a Specific Time

If you want to run at specific hours (e.g., 2:00, 4:00, 6:00, etc.):

```
0 0,2,4,6,8,10,12,14,16,18,20,22 * * * /full/path/to/your/run_wallet_monitor.sh
```

Or to start at a specific hour (e.g., 1:00, 3:00, 5:00, etc.):

```
0 1,3,5,7,9,11,13,15,17,19,21,23 * * * /full/path/to/your/run_wallet_monitor.sh
``` 