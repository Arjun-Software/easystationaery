
module.exports = {
  apps : [{
    name: 'testbluebird',
    script: 'manage.py',
    args: 'runserver 0.0.0.0:9355',
    instances: 1,
    autorestart: true,
    exp_backoff_restart_delay: 100,
    watch: false,
    max_memory_restart: '1G',
    interpreter:'/usr/bin/python3'
  }]
};



