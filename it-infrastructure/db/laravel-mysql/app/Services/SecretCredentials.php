<?php

namespace App\Services;

use App\Exceptions\InfrastructureUnavailable;
use Aws\Exception\AwsException;
use Aws\Exception\CredentialsException;
use Aws\SecretsManager\SecretsManagerClient;
use JsonException;
use Throwable;

class SecretCredentials
{
    public function __construct(private SecretsManagerClient $client) {}

    /** @return array{username:string,password:string} */
    public function get(): array
    {
        $arn = config('infrastructure.secret_arn');
        if (! is_string($arn) || ! str_starts_with($arn, 'arn:')) {
            throw new InfrastructureUnavailable('Укажіть ARN секрета в DB_SECRET_ARN.');
        }
        try {
            $result = $this->client->getSecretValue(['SecretId' => $arn, 'VersionStage' => 'AWSCURRENT']);
            $secret = json_decode($result['SecretString'] ?? '', true, flags: JSON_THROW_ON_ERROR);
            if (! is_array($secret) || ! is_string($secret['username'] ?? null) || ! is_string($secret['password'] ?? null)
                || $secret['username'] === '' || $secret['password'] === '') {
                throw new InfrastructureUnavailable('Секрет має містити непорожні username та password.');
            }

            return ['username' => $secret['username'], 'password' => $secret['password']];
        } catch (InfrastructureUnavailable $error) {
            throw $error;
        } catch (CredentialsException) {
            throw new InfrastructureUnavailable('EC2 credentials: не отримано тимчасові облікові дані. Перевірте IAM instance profile та доступ до IMDSv2.');
        } catch (AwsException $error) {
            $message = match ($error->getAwsErrorCode()) {
                'AccessDeniedException' => 'Secrets Manager: AccessDeniedException. Перевірте GetSecretValue, resource policy та KMS.',
                'ResourceNotFoundException' => 'Secrets Manager: ResourceNotFoundException. Перевірте ARN, регіон та наявність секрета.',
                'DecryptionFailure' => 'Secrets Manager: DecryptionFailure. Перевірте доступ до KMS-ключа.',
                'InvalidRequestException' => 'Secrets Manager: InvalidRequestException. Перевірте стан секрета та версії AWSCURRENT.',
                default => 'Secrets Manager: запит API не виконано. Перевірте HTTPS-доступ, регіон та стан сервісу.',
            };
            throw new InfrastructureUnavailable($message);
        } catch (JsonException) {
            throw new InfrastructureUnavailable('Secrets Manager: SecretString має бути коректним JSON із username та password.');
        } catch (Throwable) {
            throw new InfrastructureUnavailable('Не вдалося отримати секрет. Перевірте роль EC2, IMDSv2, ARN, регіон, KMS та HTTPS-доступ.');
        }
    }
}
