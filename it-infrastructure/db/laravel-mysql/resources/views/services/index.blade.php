@extends('layout')
@section('content')
<section class="hero"><div><p class="eyebrow">Огляд інфраструктури</p><h1>Сервіси<br>під контролем.</h1><p class="lead">Один каталог для середовищ, станів і приміток вашої команди.</p></div>
<aside class="overview" aria-label="Загальний стан каталогу"><div class="total"><strong>{{ $counts->sum() }}</strong><span>сервісів<br>у каталозі</span></div>
@foreach(\App\Models\Service::STATUSES as $key=>$label)<div class="count"><span><i class="dot {{ $key }}" aria-hidden="true"></i>{{ $label }}</span><strong>{{ $counts[$key] ?? 0 }}</strong></div>@endforeach</aside></section>
<section class="catalog" aria-labelledby="catalog-title"><div class="section-heading"><h2 id="catalog-title">Каталог сервісів</h2><span class="muted">{{ $services->total() }} за поточним запитом</span></div>
<form class="filters" method="get" action="{{ route('services.index') }}"><div class="field"><label for="q">Назва сервісу</label><input id="q" name="q" type="search" maxlength="120" value="{{ $filters['q'] ?? '' }}" placeholder="Знайти в каталозі"></div>
<div class="field"><label for="status">Стан</label><select id="status" name="status"><option value="">Усі стани</option>@foreach(\App\Models\Service::STATUSES as $key=>$label)<option value="{{ $key }}" @selected(($filters['status'] ?? '')===$key)>{{ $label }}</option>@endforeach</select></div>
<button type="submit" class="button secondary">Знайти</button>@if(!empty($filters['q']) || !empty($filters['status']))<a class="text-link" href="{{ route('services.index') }}">Скинути</a>@endif</form>
@if($errors->any())<p class="error" role="alert">{{ $errors->first() }}</p>@endif
<div class="service-list">@forelse($services as $service)<article class="service-row"><span class="row-id" aria-hidden="true">{{ str_pad($service->id,2,'0',STR_PAD_LEFT) }}</span>
<div class="service-name"><h3><a href="{{ route('services.show',$service) }}">{{ $service->name }}</a></h3><p>{{ \App\Models\Service::ENVIRONMENTS[$service->environment] }}</p></div>
<span class="badge {{ $service->status }}"><i class="dot {{ $service->status }}" aria-hidden="true"></i>{{ \App\Models\Service::STATUSES[$service->status] }}</span>
<a class="row-link" href="{{ route('services.show',$service) }}"><span>Переглянути</span> <span aria-hidden="true">↗</span><span class="sr-only"> {{ $service->name }}</span></a></article>
@empty<div class="empty"><h3>Тут поки немає сервісів</h3><p>Додайте перший запис або змініть умови пошуку.</p><a class="button" href="{{ route('services.create') }}">Додати сервіс</a></div>@endforelse</div>
@if($services->hasPages())<nav class="pagination" aria-label="Сторінки каталогу">@if($services->previousPageUrl())<a href="{{ $services->previousPageUrl() }}">← Попередня</a>@else<span></span>@endif
<span>{{ $services->currentPage() }} / {{ $services->lastPage() }}</span>@if($services->nextPageUrl())<a href="{{ $services->nextPageUrl() }}">Наступна →</a>@else<span></span>@endif</nav>@endif
</section>
@endsection
