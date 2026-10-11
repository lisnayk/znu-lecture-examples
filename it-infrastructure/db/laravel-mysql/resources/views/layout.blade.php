<!doctype html>
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>@yield('title','Каталог сервісів') · IT-інфраструктура</title><link rel="stylesheet" href="{{ asset('app.css') }}"></head>
<body><a class="skip" href="#content">Перейти до вмісту</a>
<header class="header"><a class="brand" href="{{ route('home') }}"><span class="mark" aria-hidden="true">і</span><span>Каталог<br><small>інфраструктури</small></span></a>
<nav aria-label="Основна навігація"><a href="{{ route('services.index') }}">Усі сервіси</a><a class="button small" href="{{ route('services.create') }}">Додати сервіс <span aria-hidden="true">+</span></a></nav></header>
<main id="content">@if(session('notice'))<p class="notice" role="status">{{ session('notice') }}</p>@endif @yield('content')</main>
<footer class="footer"><span>IT-інфраструктура · Навчальний каталог</span><span>Стан сервісів оновлюється вручну</span></footer>
</body></html>
