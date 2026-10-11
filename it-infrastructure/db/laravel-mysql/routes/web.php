<?php

use App\Http\Controllers\ServiceController;
use Illuminate\Support\Facades\Route;

Route::pattern('service', '[0-9]+');
Route::get('/', [ServiceController::class, 'index'])->name('home');
Route::get('/services/{service}/remove', [ServiceController::class, 'confirmDelete'])->name('services.confirm-delete');
Route::resource('services', ServiceController::class);
