[![Lifecycle:Stable](https://img.shields.io/badge/Lifecycle-Stable-97ca00)](<Redirect-URL>)

# ReHCh: *(Replication Health Check)*

## Script current status
Replication Health Check is currently maintained by DSS-DPS team.
All feature development are currently on hold.

## Script description
Script is set up to report on configuration anomalies in how our replication
systems are configured.  Checks will include:

Features Completed in latest version:
* list of disabled schedules - **completed**
* list of fmws in our scheduled repository that are not associated with 
  a schedule - **completed**
* identify scheduled jobs that are referencing files on E:\ drive **completed**
* scripts that do not replicate to our prod environment **completed**
* identify scheduled replications that have 0 records in destination - **completed**

~~Features Outstanding (need to be discussed!):~~
~~* check that kirk schedules all have unique ids~~
~~* list schedules that use SDE30 writers~~
~~* list of datasets with SE_ANNO_CAD data~~
~~* check for FFS files~~

Initially results will be sent via email.
