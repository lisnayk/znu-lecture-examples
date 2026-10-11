@extends('layout')
@section('title','Видалення сервісу')
@section('content')
<div class="page-heading narrow"><a class="back" href="{{ route('services.show',$service) }}">← До запису</a><p class="eyebrow">Видалення запису</p><h1>Видалити<br>цей сервіс?</h1><p class="lead">Запис «{{ $service->name }}» буде видалено з каталогу. Ця дія не видаляє ресурси AWS.</p><form method="post" action="{{ route('services.destroy',$service) }}">@csrf @method('DELETE')<div class="form-actions"><button type="submit" class="button danger">Видалити запис</button><a class="text-link" href="{{ route('services.show',$service) }}">Залишити сервіс</a></div></form></div>
@endsection
