<?php

namespace App\Exceptions;

use PDOException;
use RuntimeException;

class InfrastructureUnavailable extends RuntimeException
{
    public static function fromPdo(PDOException $error, string $stage = 'MySQL connection'): self
    {
        $state = (string) ($error->errorInfo[0] ?? $error->getCode());
        $state = preg_match('/\A[A-Z0-9]{5}\z/', $state) === 1 ? $state : 'unknown';
        $driverCode = (int) ($error->errorInfo[1] ?? 0);
        $hint = match ($driverCode) {
            1044, 1142 => 'Перевірте SQL-права користувача на базу.',
            1045 => 'Перевірте пароль, користувача та секрет у RDS Proxy.',
            1049 => 'SQL-база не існує. Перевірте DB_DATABASE.',
            2002, 2003 => 'Перевірте endpoint, порт 3306, SG, маршрути та target проксі.',
            2005 => 'Не вдалося визначити адресу endpoint. Перевірте DNS.',
            2026 => 'Перевірте TLS, CA та відповідність hostname сертифікату.',
            default => 'Перевірте target проксі, мережу, TLS та SQL-права.',
        };

        return new self(sprintf('%s: SQLSTATE=%s; MySQL=%d. %s', $stage, $state, $driverCode, $hint));
    }
}
