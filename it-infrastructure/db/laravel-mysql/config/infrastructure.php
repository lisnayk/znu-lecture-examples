<?php

return ['auth_mode' => env('DB_AUTH_MODE', 'secrets'), 'region' => env('AWS_REGION', 'us-east-1'),
    'secret_arn' => env('DB_SECRET_ARN'), 'ca_file' => env('DB_SSL_CA', '/etc/ssl/certs/ca-certificates.crt')];
