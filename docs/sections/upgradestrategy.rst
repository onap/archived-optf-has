..
 This work is licensed under a Creative Commons Attribution 4.0
 International License.

================
Upgrade Strategy
================

HAS can be upgraded in place(remove and replace) or using a blue-green
strategy.

There is no database migration required.

Supporting Facts
================

HAS only stores the info and status of the incoming homing requests. It
leverages MUSIC APIs for storing this information. It also leverages
MUSIC for communication among the HAS components. So, redeploying HAS
will not impact the data stored in MUSIC.  
