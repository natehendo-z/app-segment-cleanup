# app-segment-cleanup.py
Removes duplicate application segments with "-#" appended to name.


# Problem statement
## What's the problem?:
We have found that some clients are reporting that duplicate application segments are being generated with "-#" appended at the end of the name, i.e. HS-Servers-inbound-1, HS-Servers-inbound-2, etc.  This causes policy bloat and clutters app segment list.



## Why does it happen?:
When the auto-segment workflow runs on a host segment that aready has existing application segments, it will generate a duplicate of the same name with "-#" appended.  Some duplicates have been found up to "-7" where this has occured multiple times.


## How is it reproduced
I am only aware of one way to reproduce this issue manually in lab.
1. Auto-segment host segment
2. Disable perimeter protection on host segment
3. Repeat

Doing this multiple times will produce more duplicate segments.

# Cleanup Script
