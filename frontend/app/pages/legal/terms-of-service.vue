<script setup lang="ts">
import type { ContentTocLink } from "@nuxt/ui";

definePageMeta({ layout: "default" });

const { locale } = useI18n();
const isEn = computed(() => locale.value === "en");
const T = (ru: string, en: string) => (isEn.value ? en : ru);

useHead({
  title: () => T("Пользовательское соглашение", "Terms of Service"),
});

const tocLinks = computed<ContentTocLink[]>(() => [
  { id: "general", text: T("1. Общие положения", "1. General provisions"), depth: 2 },
  { id: "definitions", text: T("2. Термины", "2. Definitions"), depth: 2 },
  { id: "service", text: T("3. Предмет соглашения", "3. Scope"), depth: 2 },
  { id: "account", text: T("4. Регистрация и аккаунт", "4. Registration and account"), depth: 2 },
  { id: "rules", text: T("5. Правила использования", "5. Usage rules"), depth: 2 },
  { id: "content", text: T("6. Пользовательский контент", "6. User content"), depth: 2 },
  { id: "liability", text: T("7. Ограничение ответственности", "7. Limitation of liability"), depth: 2 },
  { id: "termination", text: T("8. Прекращение соглашения", "8. Termination"), depth: 2 },
  { id: "changes", text: T("9. Изменение условий", "9. Changes"), depth: 2 },
  { id: "contact", text: T("10. Контактная информация", "10. Contact information"), depth: 2 },
]);

const meta = computed(() => [
  { label: T("Сайт", "Website"), value: "dreamteams.luba.skin" },
  { label: T("Место", "Location"), value: T("г. Москва, Российская Федерация", "Moscow, Russian Federation") },
  { label: T("Дата вступления в силу", "Effective date"), value: T("22 апреля 2026 г.", "22 April 2026") },
  { label: T("Оператор", "Operator"), value: T("Любавский И. А.", "I. A. Lyubavsky") },
]);
</script>

<template>
  <UPage>
    <UContainer class="!max-w-4xl py-10 sm:py-12">
      <NuxtLink to="/"
        class="inline-flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-primary-500 dark:hover:text-primary-400 transition-colors mb-8">
        <UIcon name="i-heroicons-chevron-left" class="size-4" />
        {{ T("На главную", "Back to home") }}
      </NuxtLink>

      <header class="mb-10">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-primary-500 mb-4">
          {{ T("Правовая информация", "Legal information") }}
        </p>
        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white leading-tight tracking-tight mb-4">
          {{ T("Пользовательское соглашение", "Terms of Service") }}
        </h1>
        <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
          {{ T(
            "Документ регулирует условия использования сайта DreamTeams, права и обязанности Пользователя и Оператора.",
            "This document governs the conditions of using the DreamTeams website and defines the rights and obligations of the User and the Operator."
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
              "Настоящее Пользовательское соглашение (далее — «Соглашение») регулирует отношения между Оператором сайта dreamteams.luba.skin (далее — «Сайт») и Пользователем в связи с использованием Сайта и сервисов, предоставляемых в его рамках.",
              "This Terms of Service (the “Agreement”) governs the relationship between the Operator of the website dreamteams.luba.skin (the “Site”) and the User in connection with the use of the Site and services provided through it."
            ) }}</p>
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">1.2.</span>{{ T("Оператор: ", "Operator: ") }}<strong class="text-gray-900 dark:text-white">{{ T("Любавский Илья Андреевич", "Ilya Andreevich Lyubavsky") }}</strong>{{ T(", физическое лицо, г. Москва, Российская Федерация. Email: ", ", a natural person, Moscow, Russian Federation. Email: ") }}<strong class="text-gray-900 dark:text-white">structnull@yandex.ru</strong>.
            </p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">1.3.</span>{{ T(
              "Начало использования Сайта Пользователем означает полное и безоговорочное принятие условий настоящего Соглашения. В случае несогласия с условиями Пользователь обязан прекратить использование Сайта.",
              "By starting to use the Site, the User fully and unconditionally accepts the terms of this Agreement. If the User does not agree, they must stop using the Site."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">1.4.</span>{{ T(
              "Сайт представляет собой некоммерческий проект — агрегатор IT-соревнований и платформу для формирования команд.",
              "The Site is a non-commercial project — an IT-competition aggregator and a team-formation platform."
            ) }}</p>
          </div>
        </section>

        <section id="definitions" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">02</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Термины и определения", "Definitions") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <dl class="space-y-3">
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Пользователь", "User") }}</dt>
                <dd class="text-sm">{{ T(
                  "физическое лицо, использующее Сайт, в том числе прошедшее регистрацию и получившее статус Участника или Организатора.",
                  "a natural person who uses the Site, including one who has registered and has been granted Participant or Organizer status."
                ) }}</dd>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Участник", "Participant") }}</dt>
                <dd class="text-sm">{{ T(
                  "Пользователь, зарегистрированный с соответствующей ролью и использующий Сайт для поиска соревнований и команд.",
                  "a User registered with the corresponding role who uses the Site to find competitions and teams."
                ) }}</dd>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Организатор", "Organizer") }}</dt>
                <dd class="text-sm">{{ T(
                  "Пользователь, зарегистрированный с соответствующей ролью и публикующий на Сайте сведения о собственных IT-соревнованиях.",
                  "a User registered with the corresponding role who publishes information about their own IT competitions on the Site."
                ) }}</dd>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Контент", "Content") }}</dt>
                <dd class="text-sm">{{ T(
                  "любая информация, размещаемая Пользователем на Сайте — тексты, изображения, ссылки, описания соревнований и заявок.",
                  "any information published by a User on the Site — texts, images, links, competition descriptions and applications."
                ) }}</dd>
              </div>
            </dl>
          </div>
        </section>

        <section id="service" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">03</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Предмет Соглашения", "Scope of the Agreement") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">3.1.</span>{{ T(
              "Оператор предоставляет Пользователю безвозмездный доступ к функциональным возможностям Сайта при условии соблюдения настоящего Соглашения.",
              "The Operator grants the User free access to the Site's functionality, subject to compliance with this Agreement."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">3.2.</span>{{ T("Функциональные возможности Сайта включают, в частности:", "The Site's functionality includes, in particular:") }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("просмотр списка IT-соревнований и их подробных карточек;", "viewing the list of IT competitions and their detail pages;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("регистрацию профиля Участника и подачу заявок на соревнования;", "creating a Participant profile and submitting applications to competitions;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("регистрацию профиля Организатора и публикацию соревнований при наличии инвайт-кода;", "creating an Organizer profile and publishing competitions with a valid invite code;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("управление собственными соревнованиями, формами заявок и входящими заявками.", "managing your own competitions, application forms and incoming applications.") }}</span>
              </li>
            </ul>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">3.3.</span>{{ T(
              "Оператор вправе в любой момент изменять состав и содержание функциональных возможностей Сайта без предварительного уведомления Пользователя.",
              "The Operator may change the Site's functionality at any time without prior notice to the User."
            ) }}</p>
          </div>
        </section>

        <section id="account" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">04</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Регистрация и аккаунт", "Registration and account") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.1.</span>{{ T(
              "Регистрация на Сайте осуществляется через внешнего провайдера идентификации. При регистрации Пользователь обязуется предоставлять достоверные и полные сведения.",
              "Registration on the Site is performed via an external identity provider. At registration, the User undertakes to provide accurate and complete information."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.2.</span>{{ T(
              "Пользователь самостоятельно несёт ответственность за сохранность своих учётных данных и за все действия, совершённые с его аккаунта.",
              "The User is solely responsible for keeping their credentials safe and for all actions performed through their account."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.3.</span>{{ T(
              "Регистрация в качестве Организатора возможна только при наличии действительного инвайт-кода, выданного администратором платформы.",
              "Registration as an Organizer is only possible with a valid invite code issued by a platform administrator."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.4.</span>{{ T(
              "Пользователь вправе в любой момент удалить свой профиль. Удаление профиля приводит к безвозвратной потере связанных с ним данных.",
              "The User may delete their profile at any time. Deleting the profile results in the irreversible loss of all associated data."
            ) }}</p>
          </div>
        </section>

        <section id="rules" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">05</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Правила использования", "Usage rules") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">5.1.</span>{{ T("Пользователь обязуется не использовать Сайт для:", "The User agrees not to use the Site to:") }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-x-circle" class="size-5 text-error-500 shrink-0 mt-0.5" />
                <span>{{ T(
                  "размещения материалов, нарушающих законодательство Российской Федерации, права третьих лиц или нормы морали;",
                  "publish materials that violate the laws of the Russian Federation, third-party rights, or generally accepted moral standards;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-x-circle" class="size-5 text-error-500 shrink-0 mt-0.5" />
                <span>{{ T("распространения спама, рекламы, вредоносного программного обеспечения;", "distribute spam, advertising, or malicious software;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-x-circle" class="size-5 text-error-500 shrink-0 mt-0.5" />
                <span>{{ T(
                  "автоматизированного сбора данных, попыток получения несанкционированного доступа к чужим аккаунтам или системам Оператора;",
                  "perform automated data scraping, or attempt unauthorized access to other users' accounts or the Operator's systems;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-x-circle" class="size-5 text-error-500 shrink-0 mt-0.5" />
                <span>{{ T(
                  "намеренного создания повышенной нагрузки, препятствующей работе Сайта для других Пользователей.",
                  "intentionally generate excessive load that interferes with the Site's operation for other Users."
                ) }}</span>
              </li>
            </ul>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">5.2.</span>{{ T(
              "Нарушение правил использования может повлечь блокировку аккаунта без предварительного уведомления.",
              "Violation of the usage rules may result in the account being blocked without prior notice."
            ) }}</p>
          </div>
        </section>

        <section id="content" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">06</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Пользовательский контент", "User content") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.1.</span>{{ T(
              "Пользователь самостоятельно и в полной мере отвечает за содержание размещаемого им Контента, включая достоверность сведений о соревнованиях, анкетных данных и контактов.",
              "The User is solely and fully responsible for the content they publish, including the accuracy of competition information, profile data and contact details."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.2.</span>{{ T(
              "Размещая Контент, Пользователь подтверждает наличие у него всех прав, необходимых для его публикации, и предоставляет Оператору безвозмездную лицензию на использование такого Контента в целях функционирования Сайта.",
              "By publishing Content, the User warrants that they hold all rights necessary to publish it and grants the Operator a free-of-charge license to use the Content for the purposes of operating the Site."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.3.</span>{{ T(
              "Оператор вправе без объяснения причин удалять Контент, нарушающий настоящее Соглашение или законодательство Российской Федерации.",
              "The Operator may, without explanation, remove any Content that violates this Agreement or the laws of the Russian Federation."
            ) }}</p>
          </div>
        </section>

        <section id="liability" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">07</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Ограничение ответственности", "Limitation of liability") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">7.1.</span>{{ T(
              "Сайт предоставляется «как есть» (as is). Оператор не гарантирует бесперебойную и безошибочную работу Сайта и не несёт ответственности за убытки, возникшие вследствие его недоступности.",
              "The Site is provided “as is”. The Operator makes no guarantee of uninterrupted or error-free operation and is not liable for losses caused by downtime."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">7.2.</span>{{ T(
              "Оператор не является организатором публикуемых на Сайте соревнований и не отвечает за их проведение, сроки, призовой фонд или действия Организаторов и Участников.",
              "The Operator is not the organizer of competitions listed on the Site and is not responsible for their conduct, schedule, prize fund, or actions of Organizers and Participants."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">7.3.</span>{{ T(
              "Оператор не отвечает за содержание Контента, размещаемого Пользователями, и за достоверность указанных ими контактных данных.",
              "The Operator is not responsible for the Content published by Users or for the accuracy of the contact details they provide."
            ) }}</p>
          </div>
        </section>

        <section id="termination" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">08</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Прекращение Соглашения", "Termination") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">8.1.</span>{{ T(
              "Пользователь вправе в любой момент прекратить использование Сайта и удалить свой профиль. Это означает расторжение настоящего Соглашения по инициативе Пользователя.",
              "The User may stop using the Site and delete their profile at any time. Doing so terminates this Agreement at the User's initiative."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">8.2.</span>{{ T(
              "Оператор вправе в одностороннем порядке расторгнуть Соглашение с конкретным Пользователем в случае нарушения его условий, путём блокировки или удаления аккаунта.",
              "The Operator may unilaterally terminate the Agreement with a specific User in case of a violation, by blocking or deleting their account."
            ) }}</p>
          </div>
        </section>

        <section id="changes" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">09</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Изменение условий", "Changes to the Agreement") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">9.1.</span>{{ T(
              "Оператор вправе в любой момент вносить изменения в настоящее Соглашение. Новая редакция вступает в силу с момента её размещения на Сайте, если иное не указано в самой редакции.",
              "The Operator may amend this Agreement at any time. A new version takes effect upon publication on the Site unless the new version specifies otherwise."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">9.2.</span>{{ T(
              "Продолжение использования Сайта после внесения изменений означает согласие Пользователя с новой редакцией.",
              "Continued use of the Site after the changes constitutes the User's acceptance of the new version."
            ) }}</p>
          </div>
        </section>

        <section id="contact" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">10</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Контактная информация", "Contact information") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">10.1.</span>{{ T("По всем вопросам, связанным с настоящим Соглашением, Пользователь может обратиться к Оператору по адресу электронной почты: ", "For any questions regarding this Agreement, the User may contact the Operator by email: ") }}<strong class="text-gray-900 dark:text-white">structnull@yandex.ru</strong>.
            </p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">10.2.</span>{{ T(
              "Действующая редакция Соглашения находится в свободном доступе по адресу: https://dreamteams.luba.skin/legal/terms-of-service",
              "The current version of the Agreement is freely available at: https://dreamteams.luba.skin/legal/terms-of-service"
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
              {{ T("По любым вопросам, связанным с Соглашением.", "For any questions regarding this Agreement.") }}
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
