# idle-exporter
Simple idle (Terminal) statistic exporter for Linux based on Prometheus Python Client.

This can be used to monitor terminal activities on pods to determine if a pod is truly idle. This is meant to supplement other metrics from prometheus like GPU and CPU utilisation. Terminal last used data is usually not available on standard exporters as far as I know.

This exporter has 3 metrics:
```
user_input_idle_time:
Time since last user input, based on /dev/pts/* modification time
You can view this information with the 'stat /dev/pts/*' command

avg_user_input_idle_time:
Time since last user input, similar to user_input_idle_time.
However, this provides a 1 minute average based on 1 second polls to improve reliability.
This is to mitigate innaccurate times due to long prometheus polling rates.

user_w_idle_time:
Time since last user input based on w.
This uses a subprocess call to w and parses the return information.
The 2 metrics above take the most recent modification time in /dev/pts/* but w only checks for some specific user related terminals. This may not give you the expected idle time in some situations.

The 'process' label shows the WHAT Field of the w command, this can be useful to identify importance processes. (and not kill them mistakenly)
```



## Getting Started

This guide will help you create and run a docker container with the exporter running inside and briefly explain how to set up prometheus to pull data from the exporter.

You will require prometheus, prometheus_client and a docker daemon running for this to work.

https://github.com/prometheus/client_python

https://docs.docker.com/install/linux/docker-ce/ubuntu/


### Installing

To run, build the docker image and run it with the Makefile commands. You may need to add sudo at the start.
```
make docker
make docker-run
```

Once done, you can visit http://localhost:3003/ to check if it is serving to that endpoint.
If all goes well, you should see the following at the bottom.

```

# HELP user_input_idle_time Time since last user input, based on /dev/pts mod time
# TYPE user_input_idle_time gauge
user_input_idle_time 14.945897
# HELP avg_user_input_idle_time Time since last user input, 1 minute average based on 1 second polls to improve reliability regardless of prometheus poll rate, based on /dev/pts mod time
# TYPE avg_user_input_idle_time gauge
avg_user_input_idle_time 11.900574714285712
# HELP user_w_idle_time Time since last user input based on w, process label shows the WHAT Field of w
# TYPE user_w_idle_time gauge
user_w_idle_time{process="/sbin/upstart"} 24.0
```

To connect the exporter to prometheus, the following will help
https://prometheus.io/docs/prometheus/latest/getting_started/

Add something like this to the prometheus.yml file.
```
scrape_configs:
  - job_name: 'idle_exporter'
  
    static_configs:
    - targets: ['localhost:3003']
```

Finally start prometheus
```
cd prometheus_file_that_you_downloaded
./prometheus --config.file=prometheus.yml
```

Go to http://localhost:9090/graph and you should see your prometheus graph UI running

Under the queries you should now be able to access the following:
user_input_idle_time
avg_user_input_idle_time
user_w_idle_time


### Notes
This implementation is based of file modification times in /dev/pts as well as information from the w command.

There is normally nobody logged into a new docker container and user_w_idle_time will return default values. To try this, you can run the exporter locally.

This tracks the last terminal change and if a user is watching logs etc it refresh the idle time.