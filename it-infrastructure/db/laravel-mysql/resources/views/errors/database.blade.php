@extends('layout')
@section('title','База даних недоступна')
@section('content')
<div class="page-heading narrow"><p class="eyebrow">З’єднання з базою</p><h1>Каталог<br>тимчасово недоступний.</h1><p class="lead">Не вдалося виконати запит до бази даних. Спробуйте відкрити каталог пізніше.</p><a class="button" href="{{ route('home') }}">Спробувати знову</a></div>
@endsection
