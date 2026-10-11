<?php

use App\Exceptions\InfrastructureUnavailable;
use App\Http\Middleware\SecurityHeaders;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(web: __DIR__.'/../routes/web.php', commands: __DIR__.'/../routes/console.php', health: '/up')
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->append(SecurityHeaders::class);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->dontReport([InfrastructureUnavailable::class, QueryException::class, PDOException::class]);
        $exceptions->render(function (InfrastructureUnavailable|QueryException|PDOException $error, Request $request) {
            if ($request->expectsJson()) {
                return response()->json(['message' => 'База даних тимчасово недоступна.'], 503);
            }

            return response()->view('errors.database', [], 503);
        });
    })->create();
