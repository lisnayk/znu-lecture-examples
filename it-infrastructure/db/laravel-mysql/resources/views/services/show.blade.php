@extends('layout')
@section('title',$service->name)
@section('content')
<div class="page-heading"><a class="back" href="{{ route('services.index') }}">← До каталогу</a><p class="eyebrow">Запис № {{ $service->id }}</p><h1>{{ $service->name }}</h1><span class="badge {{ $service->status }}"><i class="dot {{ $service->status }}" aria-hidden="true"></i>{{ \App\Models\Service::STATUSES[$service->status] }}</span></div>
<div class="detail-layout"><section class="detail"><h2>Про сервіс</h2><p class="description">{{ $service->description ?: 'Примітку ще не додано.' }}</p><div class="form-actions"><a class="button" href="{{ route('services.edit',$service) }}">Редагувати</a><a class="text-link danger-link" href="{{ route('services.confirm-delete',$service) }}">Видалити запис</a></div></section>
<dl class="metadata"><div><dt>Середовище</dt><dd>{{ \App\Models\Service::ENVIRONMENTS[$service->environment] }}</dd></div><div><dt>Додано</dt><dd>{{ $service->created_at->format('d.m.Y H:i') }}</dd></div><div><dt>Оновлено</dt><dd>{{ $service->updated_at->format('d.m.Y H:i') }}</dd></div></dl></div>
@endsection
