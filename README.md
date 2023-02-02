# app-segment-cleanup.py
Removes duplicate application segments with "-#" appended to name.


## What's the problem?
Clients reporting that duplicate application segments are being generated with "-#" appended at the end of the name, i.e. HS-Servers-inbound-1, HS-Servers-inbound-2, etc.  This causes policy bloat and clutters app segment list.



## Why does it happen?
When the auto-segment workflow runs on a host segment that aready has existing application segments, it will generate a duplicate of the same name with "-#" appended.  Some duplicates have been found up to "-7" where this has occured multiple times.


## How is it reproduced?
I am only aware of one way to reproduce this issue manually in lab.
1. Auto-segment host segment
2. Disable perimeter protection on host segment
3. Repeat

Doing this multiple times will produce more duplicate segments.

## Cleanup Script Instructions

**Setup:**

This script is designed to be run from within the api-examples/v1/python/ repo.  This script is dependent on config.yaml, edgeutils.py, cert.pem, and key.pem.  Modify your config.yaml to represent the site/customer you are connecting to.

**Documentation:**

All functions are documented in the code comments.  

**Script outcome:**
- Find all app segments that have associated "-#" segments. (duplicates)
- Allow setting and clearing a filter to limit search results.  If there is a filter, merge and delete operations will only execute against what search   returns.
- Merge and Delete (Option 3)
  - Combines appNames, hosts, collectionsForHosts, and collectionsForApps across all duplicate segments and merges them to the orignal base segment.
  - Deletes associated duplicate segments
- Merge Only (Option 4)
  - Combines appNames, hosts, collectionsForHosts, and collectionsForApps across all duplicate segments and merges them to the orignal base segment.
  - Does not delete duplicate segments
- Delete Only (Option 5)
  - Does not merge to base segment
  - Deletes associated duplicate segments







