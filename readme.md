# ReHCh: *(Replication Health Check)*

Script is set up to report on configuration anomalies in how our replication
systems are configured.  Checks will include:

* list of disabled schedules - **completed**
* list of fmws in our scheduled repository that are not associated with 
  a schedule - **completed**
* identify scheduled jobs that are referencing files on E:\ drive **completed**
* scripts that do not replicate to our prod environment **completed**
* list schedules that use SDE30 writers 
* list of datasets with SE_ANNO_CAD data - **working**
* check that kirk schedules all have unique ids
* check jobs that have 0 records in the destination.
* check for FFS files

Initially results will be sent via email.
