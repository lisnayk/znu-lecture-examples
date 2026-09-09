<script setup>
// ── SiteIntro ─────────────────────────────────────────────────────
// Заголовок колекції. Тексту небагато, але він має власну розкладку,
// тому живе окремо від App.
</script>

<template>
  <section class="intro">
    <div class="intro__heading">
      <p class="intro__eyebrow">Колекція 001 · Архітектура та природа</p>
      <h1 class="intro__title">Світло <em>і</em> простір</h1>
    </div>

    <!-- Ручних переносів рядка тут немає: де рветься рядок,
         вирішує ширина колонки, а не автор тексту. -->
    <p class="intro__lead">
      Лінії, фактури й тихі моменти. Шість кадрів, які запрошують
      зупинитися та придивитись.
    </p>
  </section>
</template>

<style scoped lang="scss">
.intro {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 30px;
  padding: 35px 0 31px;

  @include phone {
    display: block;
    padding: 27px 0 24px;
  }
}

.intro__heading {
  min-width: 0;
}

.intro__eyebrow {
  @include micro;

  margin: 0 0 13px;
  color: var(--muted);

  @include phone {
    font-size: 8px;
  }
}

.intro__title {
  margin: 0;
  font-family: $font-display;
  font-size: clamp(46px, 5.5vw, 83px);
  font-weight: 400;
  letter-spacing: -4px;
  line-height: 1;
  text-wrap: balance;

  @include lap {
    letter-spacing: -2px;
  }

  @include phone {
    font-size: 50px;
  }
}

.intro__lead {
  max-width: 255px;
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.7;

  @include phone {
    max-width: 300px;
    margin-top: 20px;
  }
}
</style>
