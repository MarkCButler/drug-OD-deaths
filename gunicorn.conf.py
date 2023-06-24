"""Define a basic configuration for Gunicorn running in a Docker container.

Note that setting worker_tmp_dir may need to be configured in order to ensure
that a RAM-backed file system is used for the worker heartbeat check. See the
discussion at
https://docs.gunicorn.org/en/stable/faq.html#how-do-i-avoid-gunicorn-excessively-blocking-in-os-fchmod
Since the choice of worker_tmp_dir depends on the details of the docker image,
the compose file is used to configure this setting for the current project.
"""
# Send access logs to stdout and error logs to stderr, in order to facilitate
# retrieval of the logs from the container.
accesslog = '-'
errorlog = '-'

workers = 2
