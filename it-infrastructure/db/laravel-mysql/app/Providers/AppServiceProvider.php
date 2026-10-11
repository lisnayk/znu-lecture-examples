<?php

namespace App\Providers;

use App\Database\SecretsMySqlConnector;
use Aws\Credentials\CredentialProvider;
use Aws\Credentials\InstanceProfileProvider;
use Aws\SecretsManager\SecretsManagerClient;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind('db.connector.mysql', fn () => new SecretsMySqlConnector);
        $this->app->singleton(SecretsManagerClient::class, function () {
            return new SecretsManagerClient(['version' => 'latest', 'region' => config('infrastructure.region'),
                'credentials' => CredentialProvider::memoize(new InstanceProfileProvider([
                    'ec2_metadata_v1_disabled' => true, 'timeout' => 2, 'retries' => 1])),
                'http' => ['connect_timeout' => 3, 'timeout' => 6], 'retries' => 1]);
        });
    }

    public function boot(): void {}
}
