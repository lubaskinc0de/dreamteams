<script setup lang="ts">
import type { ContentTocLink } from "@nuxt/ui";

definePageMeta({ layout: "default" });

const { locale } = useI18n();
const isEn = computed(() => locale.value === "en");
const T = (ru: string, en: string) => (isEn.value ? en : ru);
const { navigateBack } = useBackNavigation("/");

useHead({
  title: () => T("Политика использования файлов cookie", "Cookie Policy"),
});

const tocLinks = computed<ContentTocLink[]>(() => [
  { id: "general", text: T("1. Общие положения", "1. General provisions"), depth: 2 },
  { id: "what", text: T("2. Что такое файлы cookie", "2. What cookies are"), depth: 2 },
  { id: "categories", text: T("3. Категории используемых cookie", "3. Cookie categories"), depth: 2 },
  { id: "third-party", text: T("4. Сторонние сервисы", "4. Third-party services"), depth: 2 },
  { id: "retention", text: T("5. Срок хранения cookie", "5. Retention periods"), depth: 2 },
  { id: "manage", text: T("6. Управление файлами cookie", "6. Managing cookies"), depth: 2 },
  { id: "processing", text: T("7. Обработка данных через cookie", "7. Processing of cookie data"), depth: 2 },
  { id: "changes", text: T("8. Изменения в Политике cookie", "8. Changes to this Policy"), depth: 2 },
  { id: "contact", text: T("9. Контактная информация", "9. Contact information"), depth: 2 },
]);

const meta = computed(() => [
  { label: T("Сайт", "Website"), value: "dreamteams.luba.skin" },
  { label: T("Место", "Location"), value: T("г. Москва, Российская Федерация", "Moscow, Russian Federation") },
  { label: T("Дата вступления в силу", "Effective date"), value: T("22 апреля 2026 г.", "22 April 2026") },
  { label: T("Оператор", "Operator"), value: T("Любавский И. А.", "I. A. Lyubavsky") },
]);

const retentionRows = computed(() => [
  { label: T("Строго необходимые (сессионные)", "Strictly necessary (session)"), value: T("до закрытия браузера", "until the browser is closed") },
  { label: T("Строго необходимые (авторизация)", "Strictly necessary (authentication)"), value: T("до 30 дней", "up to 30 days") },
  { label: T("Функциональные", "Functional"), value: T("до 12 месяцев", "up to 12 months") },
  { label: T("Аналитические", "Analytics"), value: T("до 24 месяцев", "up to 24 months") },
  { label: T("Сохранённый выбор согласия", "Stored consent choice"), value: T("до 12 месяцев", "up to 12 months") },
]);

const browsers = [
  { name: "Google Chrome", url: "https://support.google.com/chrome/answer/95647", display: "support.google.com/chrome/answer/95647" },
  { name: "Mozilla Firefox", url: "https://support.mozilla.org/kb/enhanced-tracking-protection-firefox-desktop", display: "support.mozilla.org" },
  { name: "Safari", url: "https://support.apple.com/guide/safari/manage-cookies-sfri11471/", display: "support.apple.com" },
  { name: "Microsoft Edge", url: "https://support.microsoft.com/microsoft-edge", display: "support.microsoft.com" },
  { name: "Yandex Browser", url: "https://yandex.ru/support/browser/", display: "yandex.ru/support/browser" },
];
</script>

<template>
  <UPage>
    <UContainer class="!max-w-4xl py-10 sm:py-12">
      <UButton
        icon="i-heroicons-chevron-left"
        color="neutral"
        variant="ghost"
        class="mb-8"
        @click="navigateBack()"
      >
        {{ T("Назад", "Back") }}
      </UButton>

      <header class="mb-10">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-primary-500 mb-4">
          {{ T("Правовая информация", "Legal information") }}
        </p>
        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white leading-tight tracking-tight mb-4">
          {{ T("Политика использования файлов cookie", "Cookie Policy") }}
        </h1>
        <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
          {{ T(
            "Документ разъясняет, какие файлы cookie и аналогичные технологии используются на Сайте, в каких целях они применяются и каким образом Пользователь может управлять своими настройками.",
            "This document explains what cookies and similar technologies are used on the Site, for what purposes, and how the User can manage their settings."
          ) }}
        </p>
      </header>

      <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5 rounded-2xl border border-gray-200 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-900/40 p-6 mb-14">
        <div v-for="item in meta" :key="item.label">
          <dt class="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">
            {{ item.label }}
          </dt>
          <dd class="text-sm text-gray-900 dark:text-white font-medium">
            {{ item.value }}
          </dd>
        </div>
      </dl>

      <article class="space-y-14">
        <section id="general" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">01</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Общие положения", "General provisions") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">1.1.</span>{{ T(
              "Настоящая Политика использования файлов cookie (далее — «Политика cookie») разъясняет, какие файлы cookie и аналогичные технологии используются на сайте dreamteams.luba.skin (далее — «Сайт»), в каких целях они применяются и каким образом Пользователь может управлять своими настройками.",
              "This Cookie Policy (the “Cookie Policy”) explains which cookies and similar technologies are used on dreamteams.luba.skin (the “Site”), for what purposes they are used, and how the User can manage their settings."
            ) }}</p>
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">1.2.</span>{{ T("Оператор Сайта (далее — «Оператор»): ", "Site Operator (the “Operator”): ") }}<strong class="text-gray-900 dark:text-white">{{ T("Любавский Илья Андреевич", "Ilya Andreevich Lyubavsky") }}</strong>{{ T(", физическое лицо, г. Москва, Российская Федерация. Контактный адрес электронной почты: ", ", a natural person, Moscow, Russian Federation. Contact email: ") }}<strong class="text-gray-900 dark:text-white">structnull@yandex.ru</strong>.
            </p>
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">1.3.</span>{{ T("Настоящая Политика cookie является дополнением к ", "This Cookie Policy supplements the ") }}<NuxtLink to="/legal/privacy-policy" class="text-primary-500 hover:text-primary-400 underline underline-offset-2">{{ T("Политике обработки персональных данных", "Privacy Policy") }}</NuxtLink>{{ T(" и должна рассматриваться совместно с ней.", " and should be read together with it.") }}
            </p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">1.4.</span>{{ T(
              "Продолжая использование Сайта после ознакомления с уведомлением о cookie и/или после выражения согласия через соответствующий интерфейс (cookie-баннер), Пользователь подтверждает согласие с условиями настоящей Политики в части, не относящейся к строго необходимым файлам cookie.",
              "By continuing to use the Site after receiving the cookie notice and/or after expressing consent via the cookie banner, the User confirms agreement with this Policy regarding cookies other than strictly necessary ones."
            ) }}</p>
          </div>
        </section>

        <section id="what" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">02</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Что такое файлы cookie", "What cookies are") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">2.1.</span><strong class="text-gray-900 dark:text-white">{{ T("Файлы cookie", "Cookies") }}</strong>{{ T(
              " — небольшие текстовые файлы, которые сохраняются на устройстве Пользователя (компьютере, смартфоне, планшете) веб-браузером при посещении Сайта. Cookie позволяют Сайту «запоминать» действия и предпочтения Пользователя (например, выбранный язык, параметры отображения, данные авторизации) в течение определённого времени, чтобы Пользователю не приходилось повторно вводить эти данные при каждом посещении или переходе между страницами.",
              " are small text files stored on the User's device (computer, smartphone, tablet) by the web browser when visiting the Site. Cookies allow the Site to “remember” the User's actions and preferences (such as language, display options, authentication data) for a period of time so the User does not need to re-enter them on every visit or page navigation."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">2.2.</span>{{ T("Под ", "By ") }}<strong class="text-gray-900 dark:text-white">{{ T("аналогичными технологиями", "similar technologies") }}</strong>{{ T(
              " в настоящей Политике понимаются также локальное хранилище браузера (localStorage, sessionStorage), пиксельные теги (web beacons), идентификаторы устройств и иные средства, выполняющие схожие с cookie функции.",
              " this Policy also means browser local storage (localStorage, sessionStorage), tracking pixels (web beacons), device identifiers and other means that serve a similar purpose to cookies."
            ) }}</p>

            <h3 class="text-base font-semibold text-gray-900 dark:text-white mt-6 mb-3">
              {{ T("По сроку хранения", "By retention duration") }}
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <p class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Сессионные", "Session") }}</p>
                <p class="text-sm">{{ T("удаляются автоматически при закрытии браузера.", "automatically deleted when the browser is closed.") }}</p>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <p class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Постоянные", "Persistent") }}</p>
                <p class="text-sm">{{ T(
                  "сохраняются на устройстве в течение указанного срока либо до удаления Пользователем вручную.",
                  "stored on the device for a specified period or until the User deletes them manually."
                ) }}</p>
              </div>
            </div>

            <h3 class="text-base font-semibold text-gray-900 dark:text-white mt-6 mb-3">
              {{ T("По источнику", "By source") }}
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <p class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Первичные (first-party)", "First-party") }}</p>
                <p class="text-sm">{{ T("устанавливаются непосредственно Сайтом.", "set directly by the Site.") }}</p>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <p class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Сторонние (third-party)", "Third-party") }}</p>
                <p class="text-sm">{{ T(
                  "устанавливаются внешними сервисами, подключёнными к Сайту (например, системами веб-аналитики).",
                  "set by external services connected to the Site (for example, web-analytics systems)."
                ) }}</p>
              </div>
            </div>
          </div>
        </section>

        <section id="categories" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">03</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Категории используемых cookie", "Cookie categories used") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">3.1.</span>{{ T(
              "На Сайте используются файлы cookie следующих категорий.",
              "The Site uses cookies in the following categories."
            ) }}</p>

            <div class="space-y-4">
              <div class="rounded-xl border-l-4 border-primary-500 bg-primary-500/5 p-5">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
                  {{ T("3.1.1. Строго необходимые cookie", "3.1.1. Strictly necessary cookies") }}
                </h3>
                <p class="text-sm mb-3">{{ T(
                  "Обеспечивают базовую работоспособность Сайта и не могут быть отключены в интерфейсе управления согласием. Без них невозможно корректное функционирование отдельных разделов Сайта, включая авторизацию в личном аккаунте.",
                  "Ensure the basic operation of the Site and cannot be disabled through the consent interface. Without them, some parts of the Site — including account sign-in — will not function correctly."
                ) }}</p>
                <dl class="text-sm grid grid-cols-1 sm:grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
                  <dt class="text-gray-500 dark:text-gray-400">{{ T("Назначение:", "Purpose:") }}</dt>
                  <dd>{{ T(
                    "поддержание сессии, аутентификация, защита от CSRF, сохранение выбора согласия на cookie.",
                    "maintaining the session, authentication, CSRF protection, storing cookie consent choice."
                  ) }}</dd>
                  <dt class="text-gray-500 dark:text-gray-400">{{ T("Правовое основание:", "Legal basis:") }}</dt>
                  <dd>{{ T(
                    "законный интерес Оператора; отдельного согласия не требуется.",
                    "legitimate interest of the Operator; no separate consent required."
                  ) }}</dd>
                </dl>
              </div>

              <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-5">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
                  {{ T("3.1.2. Функциональные cookie", "3.1.2. Functional cookies") }}
                </h3>
                <p class="text-sm mb-3">{{ T(
                  "Позволяют Сайту запоминать пользовательские настройки (например, выбранный язык интерфейса, параметры отображения) и предоставлять расширенные возможности.",
                  "Let the Site remember user preferences (such as the selected interface language, display options) and provide enhanced features."
                ) }}</p>
                <dl class="text-sm grid grid-cols-1 sm:grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
                  <dt class="text-gray-500 dark:text-gray-400">{{ T("Назначение:", "Purpose:") }}</dt>
                  <dd>{{ T("сохранение предпочтений Пользователя между сессиями.", "storing user preferences across sessions.") }}</dd>
                  <dt class="text-gray-500 dark:text-gray-400">{{ T("Правовое основание:", "Legal basis:") }}</dt>
                  <dd>{{ T("согласие Пользователя.", "User's consent.") }}</dd>
                </dl>
              </div>

              <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-5">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
                  {{ T("3.1.3. Аналитические cookie", "3.1.3. Analytics cookies") }}
                </h3>
                <p class="text-sm mb-3">{{ T(
                  "Используются для сбора обезличенной статистики о посещениях Сайта: количество визитов, источники трафика, популярность страниц, поведение на Сайте.",
                  "Used to collect anonymised statistics about visits to the Site: number of visits, traffic sources, popular pages, on-site behaviour."
                ) }}</p>
                <dl class="text-sm grid grid-cols-1 sm:grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
                  <dt class="text-gray-500 dark:text-gray-400">{{ T("Назначение:", "Purpose:") }}</dt>
                  <dd>{{ T("веб-аналитика, измерение аудитории.", "web analytics, audience measurement.") }}</dd>
                  <dt class="text-gray-500 dark:text-gray-400">{{ T("Правовое основание:", "Legal basis:") }}</dt>
                  <dd>{{ T("согласие Пользователя.", "User's consent.") }}</dd>
                </dl>
              </div>
            </div>

            <p class="flex items-start gap-3 rounded-lg bg-amber-500/5 border border-amber-500/20 p-4 mt-4">
              <UIcon name="i-heroicons-information-circle" class="size-5 text-amber-500 shrink-0 mt-0.5" />
              <span><span class="font-semibold text-gray-900 dark:text-white mr-1">3.2.</span>{{ T("Рекламные и маркетинговые cookie на Сайте ", "Advertising and marketing cookies are ") }}<strong class="text-gray-900 dark:text-white">{{ T("не используются", "not used") }}</strong>{{ T(
                ". Оператор не передаёт данные рекламным сетям и не осуществляет таргетирование рекламы с использованием файлов cookie.",
                " on the Site. The Operator does not share data with advertising networks and does not perform ad targeting using cookies."
              ) }}</span>
            </p>
          </div>
        </section>

        <section id="third-party" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">04</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Сторонние сервисы", "Third-party services") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.1.</span>{{ T(
              "Оператор может использовать следующие сторонние сервисы, которые могут устанавливать собственные файлы cookie:",
              "The Operator may use the following third-party services, which may set their own cookies:"
            ) }}</p>
            <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-5">
              <p class="font-semibold text-gray-900 dark:text-white mb-2">{{ T("Яндекс Метрика", "Yandex Metrica") }}</p>
              <p class="text-sm mb-2">{{ T(
                "ООО «Яндекс», Российская Федерация — для сбора обезличенной статистики посещений Сайта.",
                "Yandex LLC, Russian Federation — for collecting anonymised visit statistics."
              ) }}</p>
              <a href="https://yandex.ru/legal/confidential/" target="_blank" rel="noopener"
                class="inline-flex items-center gap-1 text-sm text-primary-500 hover:text-primary-400 underline underline-offset-2">
                {{ T("Политика конфиденциальности", "Privacy policy") }}
                <UIcon name="i-heroicons-arrow-top-right-on-square" class="size-3.5" />
              </a>
            </div>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.2.</span>{{ T(
              "Сторонние сервисы действуют на основании собственных политик конфиденциальности. Оператор не контролирует содержание и работу cookie, устанавливаемых сторонними сервисами, и рекомендует Пользователю ознакомиться с соответствующими политиками самостоятельно.",
              "Third-party services operate under their own privacy policies. The Operator does not control the content or behaviour of cookies set by third-party services and recommends that the User review the relevant policies themselves."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.3.</span>{{ T(
              "Подключение сторонних сервисов к Сайту может являться трансграничной передачей данных в значении Федерального закона от 27.07.2006 № 152-ФЗ «О персональных данных». Использование соответствующих категорий cookie осуществляется только при наличии согласия Пользователя.",
              "Use of third-party services on the Site may constitute a cross-border data transfer within the meaning of Federal Law No. 152-FZ of 27 July 2006 “On Personal Data”. Such cookies are used only with the User's consent."
            ) }}</p>
          </div>
        </section>

        <section id="retention" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">05</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Срок хранения cookie", "Retention periods") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">5.1.</span>{{ T(
              "Максимальные сроки хранения файлов cookie на устройстве Пользователя:",
              "Maximum retention periods for cookies stored on the User's device:"
            ) }}</p>
            <div class="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
              <table class="w-full text-sm">
                <tbody>
                  <tr v-for="(row, i) in retentionRows" :key="row.label"
                    :class="i % 2 === 1 ? 'bg-gray-50/60 dark:bg-gray-900/40' : ''">
                    <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">{{ row.label }}</td>
                    <td class="px-4 py-3 text-gray-600 dark:text-gray-400 text-right sm:text-left">{{ row.value }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">5.2.</span>{{ T(
              "По истечении указанных сроков файлы cookie автоматически удаляются, либо Пользователю повторно предлагается выразить согласие.",
              "After these periods expire, cookies are deleted automatically, or the User is asked to confirm consent again."
            ) }}</p>
          </div>
        </section>

        <section id="manage" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">06</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Управление файлами cookie", "Managing cookies") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.1.</span>{{ T(
              "При первом посещении Сайта Пользователю отображается уведомление (cookie-баннер) с возможностью:",
              "On the first visit to the Site, the User is shown a notice (cookie banner) with the option to:"
            ) }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T("принять все категории cookie;", "accept all cookie categories;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T("отклонить все категории, кроме строго необходимых;", "reject all categories except strictly necessary;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T("выбрать отдельные категории cookie в настройках.", "choose individual cookie categories in the settings.") }}</span>
              </li>
            </ul>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.2.</span>{{ T(
              "Пользователь вправе в любой момент изменить или отозвать ранее данное согласие, перейдя в раздел управления настройками cookie на Сайте.",
              "The User may change or withdraw their previously given consent at any time via the cookie settings on the Site."
            ) }}</p>

            <h3 class="text-base font-semibold text-gray-900 dark:text-white mt-6 mb-3">
              {{ T("Управление через браузер", "Managing via the browser") }}
            </h3>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.3.</span>{{ T(
              "Пользователь также может управлять файлами cookie через настройки своего браузера:",
              "The User may also manage cookies through their browser settings:"
            ) }}</p>
            <ul class="space-y-2">
              <li v-for="b in browsers" :key="b.name"
                class="flex items-center justify-between gap-3 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 px-4 py-3">
                <span class="font-medium text-gray-900 dark:text-white">{{ b.name }}</span>
                <a :href="b.url" target="_blank" rel="noopener"
                  class="inline-flex items-center gap-1 text-sm text-primary-500 hover:text-primary-400 underline underline-offset-2">
                  {{ b.display }}
                  <UIcon name="i-heroicons-arrow-top-right-on-square" class="size-3.5" />
                </a>
              </li>
            </ul>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.4.</span>{{ T(
              "Пользователь может настроить браузер на уведомление о получении cookie, отказ от приёма отдельных cookie или полное отключение приёма cookie. Соответствующие инструкции содержатся в документации используемого браузера.",
              "The User may configure the browser to notify them of incoming cookies, reject specific cookies, or disable cookies altogether. Relevant instructions are available in the browser's documentation."
            ) }}</p>
            <p class="flex items-start gap-3 rounded-lg bg-error-500/5 border border-error-500/20 p-4">
              <UIcon name="i-heroicons-exclamation-triangle" class="size-5 text-error-500 shrink-0 mt-0.5" />
              <span><span class="font-semibold text-gray-900 dark:text-white mr-1">6.5.</span>{{ T(
                "Отключение или блокировка строго необходимых cookie может привести к частичной или полной неработоспособности отдельных функций Сайта, включая возможность авторизации в личном аккаунте.",
                "Disabling or blocking strictly necessary cookies may partially or fully break certain Site features, including account sign-in."
              ) }}</span>
            </p>
          </div>
        </section>

        <section id="processing" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">07</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Обработка данных через cookie", "Processing of cookie data") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">7.1.</span>{{ T("Данные, получаемые с использованием файлов cookie, обрабатываются в соответствии с ", "Data obtained via cookies is processed in accordance with the Operator's ") }}<NuxtLink to="/legal/privacy-policy" class="text-primary-500 hover:text-primary-400 underline underline-offset-2">{{ T("Политикой обработки персональных данных", "Privacy Policy") }}</NuxtLink>{{ T(" Оператора.", ".") }}
            </p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">7.2.</span>{{ T(
              "Если данные, полученные через cookie, относятся к персональным данным в значении 152-ФЗ, их обработка осуществляется на правовых основаниях, предусмотренных указанным законом, в том числе — на основании согласия Пользователя.",
              "If cookie-obtained data qualifies as personal data under 152-FZ, it is processed on the legal grounds provided by that law, including the User's consent."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">7.3.</span>{{ T("Пользователь имеет право:", "The User has the right to:") }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("получать информацию об обрабатываемых данных;", "obtain information about processed data;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("требовать их уточнения, блокирования или уничтожения;", "request rectification, blocking, or erasure of such data;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("отозвать согласие на обработку;", "withdraw consent to processing;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "обратиться с жалобой в уполномоченный орган по защите прав субъектов персональных данных (Роскомнадзор).",
                  "lodge a complaint with the authorised data protection authority (Roskomnadzor)."
                ) }}</span>
              </li>
            </ul>
          </div>
        </section>

        <section id="changes" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">08</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Изменения в Политике cookie", "Changes to this Cookie Policy") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">8.1.</span>{{ T(
              "Оператор вправе вносить изменения в настоящую Политику cookie. Актуальная редакция размещается на Сайте с указанием даты вступления в силу.",
              "The Operator may amend this Cookie Policy. The current version is published on the Site with its effective date."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">8.2.</span>{{ T(
              "При существенном изменении состава используемых cookie или целей их использования Оператор повторно запрашивает согласие Пользователя через cookie-баннер.",
              "If the set of cookies used or the purposes of their use changes significantly, the Operator will re-request the User's consent via the cookie banner."
            ) }}</p>
          </div>
        </section>

        <section id="contact" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">09</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Контактная информация", "Contact information") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">9.1.</span>{{ T("По всем вопросам, связанным с использованием файлов cookie, а также для реализации прав, предусмотренных настоящей Политикой, Пользователь может обратиться к Оператору по адресу электронной почты: ", "For any questions regarding the use of cookies, or to exercise the rights set out in this Policy, the User may contact the Operator by email: ") }}<strong class="text-gray-900 dark:text-white">structnull@yandex.ru</strong>.
            </p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">9.2.</span>{{ T(
              "Действующая редакция Политики cookie находится в свободном доступе по адресу: https://dreamteams.luba.skin/",
              "The current version of the Cookie Policy is freely available at: https://dreamteams.luba.skin/"
            ) }}</p>
          </div>
        </section>
      </article>

      <aside class="mt-16 rounded-2xl border border-primary-500/20 bg-primary-500/5 p-6 sm:p-8">
        <div class="flex items-start gap-4">
          <div class="shrink-0 size-12 rounded-xl bg-primary-500/10 flex items-center justify-center">
            <UIcon name="i-heroicons-envelope" class="size-6 text-primary-500" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-gray-900 dark:text-white mb-1">
              {{ T("Контакты Оператора", "Operator contact") }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3 leading-relaxed">
              {{ T(
                "Вопросы по использованию файлов cookie и реализации ваших прав.",
                "Questions about cookies and exercising your rights."
              ) }}
            </p>
            <a href="mailto:structnull@yandex.ru"
              class="inline-flex items-center gap-1.5 text-primary-500 hover:text-primary-400 font-medium">
              structnull@yandex.ru
              <UIcon name="i-heroicons-arrow-top-right-on-square" class="size-4" />
            </a>
          </div>
        </div>
      </aside>

      <p class="mt-10 text-center text-sm text-gray-500 dark:text-gray-400 italic">
        {{ T("Оператор: Любавский И. А.", "Operator: I. A. Lyubavsky") }}
      </p>
    </UContainer>

    <template #right>
      <UContentToc :title="T('Содержание', 'Contents')" :links="tocLinks" highlight />
    </template>
  </UPage>
</template>
