import os
import sys
import fcntl  # For file locking
import time


# Function to create a lock file
def check_if_running(LOCK_FILE):
    try:
        # Open the lock file
        lockfile = open(LOCK_FILE, 'w')
        # Try to acquire an exclusive lock on the file
        fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Write the PID to the lock file for tracking (optional)
        lockfile.write(str(os.getpid()))
        lockfile.flush()
        return lockfile  # Return the file so it's not garbage collected and the lock is released
    except IOError:
        # If another process is holding the lock, exit early
        print("Script is already running. Exiting.")
        return "Running"

