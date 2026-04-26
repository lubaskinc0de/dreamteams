<script setup lang="ts">
import type { ContentTocLink } from "@nuxt/ui";

definePageMeta({ layout: "default" });

const { locale, t: i18nT } = useI18n();
const isEn = computed(() => locale.value === "en");
const T = (ru: string, en: string) => (isEn.value ? en : ru);
const { navigateBack } = useBackNavigation("/");

useHead({
  title: () => T(
    "Политика обработки персональных данных",
    "Personal Data Processing Policy",
  ),
});

const tocLinks = computed<ContentTocLink[]>(() => [
  { id: "general", text: T("1. Общие положения", "1. General provisions"), depth: 2 },
  { id: "definitions", text: T("2. Основные понятия", "2. Definitions"), depth: 2 },
  { id: "data", text: T("3. Состав обрабатываемых данных", "3. Data processed"), depth: 2 },
  { id: "purposes", text: T("4. Цели обработки", "4. Purposes of processing"), depth: 2 },
  { id: "legal-basis", text: T("5. Правовые основания", "5. Legal basis"), depth: 2 },
  { id: "conditions", text: T("6. Порядок и условия обработки", "6. Conditions of processing"), depth: 2 },
  { id: "sharing", text: T("7. Передача третьим лицам", "7. Third-party sharing"), depth: 2 },
  { id: "protection", text: T("8. Меры по защите", "8. Data protection"), depth: 2 },
  { id: "rights", text: T("9. Права Пользователя", "9. User rights"), depth: 2 },
  { id: "cookies", text: T("10. Использование cookie", "10. Cookies"), depth: 2 },
  { id: "final", text: T("11. Заключительные положения", "11. Final provisions"), depth: 2 },
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
          {{ T("Политика обработки персональных данных", "Personal Data Processing Policy") }}
        </h1>
        <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
          {{ T(
            "Документ определяет порядок обработки персональных данных пользователей сайта и меры по обеспечению их безопасности в соответствии с Федеральным законом № 152-ФЗ.",
            "This document describes how we process users' personal data and the safeguards we apply in accordance with Federal Law No. 152-FZ of the Russian Federation."
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
              "Настоящая Политика обработки персональных данных (далее — «Политика») разработана в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных» (далее — «152-ФЗ») и определяет порядок обработки персональных данных и меры по обеспечению их безопасности, принимаемые оператором.",
              "This Personal Data Processing Policy (the “Policy”) has been developed in accordance with Federal Law No. 152-FZ of 27 July 2006 “On Personal Data” (the “152-FZ”) and sets out how personal data is processed and protected by the operator."
            ) }}</p>
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">1.2.</span>{{ T(
                "Оператор персональных данных (далее — «Оператор»): ",
                "Personal data operator (the “Operator”): "
              ) }}<strong class="text-gray-900 dark:text-white">{{ T("Любавский Илья Андреевич", "Ilya Andreevich Lyubavsky") }}</strong>{{ T(
                ", физическое лицо, г. Москва, Российская Федерация. Контактный адрес электронной почты: ",
                ", a natural person, Moscow, Russian Federation. Contact email: "
              ) }}<strong class="text-gray-900 dark:text-white">structnull@yandex.ru</strong>.
            </p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">1.3.</span>{{ T(
              "Оператор осуществляет обработку персональных данных пользователей сайта dreamteams.luba.skin (далее — «Сайт») в рамках некоммерческого проекта «DreamTeams».",
              "The Operator processes personal data of users of the website dreamteams.luba.skin (the “Site”) as part of the non-commercial “DreamTeams” project."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">1.4.</span>{{ T(
              "Настоящая Политика применяется ко всей информации, которую Оператор может получить о Пользователе во время использования им Сайта, и действует в отношении всех персональных данных, обрабатываемых Оператором.",
              "This Policy applies to all information that the Operator may obtain about a User through their use of the Site, and covers all personal data processed by the Operator."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">1.5.</span>{{ T(
              "Использование Сайта Пользователем означает согласие с настоящей Политикой и условиями обработки его персональных данных. В случае несогласия с условиями Политики Пользователь должен прекратить использование Сайта.",
              "By using the Site, the User agrees to this Policy and the terms of processing of their personal data. A User who does not agree with the Policy must stop using the Site."
            ) }}</p>
          </div>
        </section>

        <section id="definitions" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">02</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Основные понятия", "Definitions") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p>{{ T("В настоящей Политике используются следующие основные понятия:", "The following terms are used in this Policy:") }}</p>
            <dl class="space-y-3">
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Персональные данные", "Personal data") }}</dt>
                <dd class="text-sm">{{ T(
                  "любая информация, относящаяся к прямо или косвенно определённому или определяемому физическому лицу (субъекту персональных данных).",
                  "any information relating to a directly or indirectly identified or identifiable natural person (data subject)."
                ) }}</dd>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Оператор", "Operator") }}</dt>
                <dd class="text-sm">{{ T(
                  "физическое лицо, указанное в п. 1.2, самостоятельно организующее и осуществляющее обработку персональных данных, а также определяющее цели и состав обрабатываемых данных.",
                  "the natural person identified in clause 1.2, who independently organises and carries out personal data processing and determines the purposes and scope of the data processed."
                ) }}</dd>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Пользователь", "User") }}</dt>
                <dd class="text-sm">{{ T(
                  "физическое лицо, посещающее Сайт и/или предоставляющее свои персональные данные через формы на Сайте.",
                  "a natural person who visits the Site and/or provides personal data through forms on the Site."
                ) }}</dd>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Обработка персональных данных", "Processing of personal data") }}</dt>
                <dd class="text-sm">{{ T(
                  "любое действие (операция) или совокупность действий, совершаемых с использованием средств автоматизации или без их использования с персональными данными, включая сбор, запись, систематизацию, накопление, хранение, уточнение, извлечение, использование, передачу, обезличивание, блокирование, удаление, уничтожение.",
                  "any operation or set of operations performed on personal data, with or without the use of automated means, including collection, recording, organisation, accumulation, storage, adaptation, retrieval, use, transfer, anonymisation, blocking, erasure, and destruction."
                ) }}</dd>
              </div>
              <div class="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/40 p-4">
                <dt class="font-semibold text-gray-900 dark:text-white mb-1">{{ T("Согласие на обработку персональных данных", "Consent to data processing") }}</dt>
                <dd class="text-sm">{{ T(
                  "свободное, конкретное, информированное и сознательное волеизъявление Пользователя, данное им в отношении обработки своих персональных данных.",
                  "a freely given, specific, informed and unambiguous indication of the User's wishes regarding the processing of their personal data."
                ) }}</dd>
              </div>
            </dl>
          </div>
        </section>

        <section id="data" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">03</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Состав обрабатываемых персональных данных", "Personal data processed") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">3.1.</span>{{ T(
              "Оператор обрабатывает следующие персональные данные, предоставляемые Пользователем при регистрации и/или подписке на рассылку обновлений:",
              "The Operator processes the following personal data provided by the User during registration and/or subscription to updates:"
            ) }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("фамилия, имя (либо иное имя/псевдоним, указанное Пользователем);", "last name, first name (or another name or alias provided by the User);") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("адрес электронной почты;", "email address;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("номер мобильного телефона.", "mobile phone number.") }}</span>
              </li>
            </ul>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">3.2.</span>{{ T(
              "Дополнительно Оператор может автоматически собирать следующие технические данные при посещении Пользователем Сайта: IP-адрес, тип и версия браузера, тип операционной системы, информация о времени посещения и страницах, которые посещает Пользователь. Указанные данные носят обезличенный характер и используются исключительно для обеспечения работоспособности Сайта.",
              "In addition, the Operator may automatically collect technical data when the User visits the Site: IP address, browser type and version, operating system, time of visit and visited pages. Such data is anonymised and used solely to maintain the Site's operation."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">3.3.</span>{{ T(
              "Оператор не обрабатывает специальные категории персональных данных (касающиеся расовой, национальной принадлежности, политических взглядов, религиозных убеждений, состояния здоровья и др.) и биометрические персональные данные.",
              "The Operator does not process special categories of personal data (concerning race, ethnicity, political views, religious beliefs, health, etc.) or biometric personal data."
            ) }}</p>
          </div>
        </section>

        <section id="purposes" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">04</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Цели обработки персональных данных", "Purposes of processing") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.1.</span>{{ T(
              "Оператор обрабатывает персональные данные Пользователя в следующих целях:",
              "The Operator processes User personal data for the following purposes:"
            ) }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "регистрация и предоставление Пользователю доступа к функциональным возможностям Сайта посредством личного аккаунта;",
                  "registering and granting the User access to the Site's functionality through a personal account;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("идентификация Пользователя при использовании Сайта;", "identifying the User while using the Site;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "отправка Пользователю информационных сообщений и уведомлений, связанных с обновлениями проекта «DreamTeams», при условии его подписки на рассылку;",
                  "sending informational messages and notifications about DreamTeams updates to subscribed Users;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("ответы на обращения и запросы Пользователя;", "responding to User enquiries and requests;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "исполнение обязанностей, возложенных на Оператора действующим законодательством Российской Федерации.",
                  "fulfilling the Operator's obligations under the applicable laws of the Russian Federation."
                ) }}</span>
              </li>
            </ul>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">4.2.</span>{{ T(
              "Оператор не использует персональные данные Пользователя в целях, не связанных с указанными выше, без получения дополнительного согласия.",
              "The Operator does not use User personal data for purposes unrelated to those listed above without obtaining additional consent."
            ) }}</p>
          </div>
        </section>

        <section id="legal-basis" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">05</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Правовые основания обработки", "Legal basis for processing") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">5.1.</span>{{ T(
              "Правовыми основаниями обработки персональных данных Оператором являются:",
              "The legal bases for the Operator's processing of personal data are:"
            ) }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "согласие Пользователя на обработку его персональных данных, выраженное путём проставления соответствующей отметки при заполнении формы на Сайте;",
                  "the User's consent to the processing of their personal data, expressed by ticking the relevant checkbox when completing a form on the Site;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "положения 152-ФЗ и иных нормативных правовых актов Российской Федерации в области защиты персональных данных.",
                  "the provisions of 152-FZ and other regulatory acts of the Russian Federation on personal data protection."
                ) }}</span>
              </li>
            </ul>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">5.2.</span>{{ T(
              "Согласие на обработку персональных данных может быть отозвано Пользователем в любой момент путём направления соответствующего запроса на адрес электронной почты, указанный в п. 1.2 настоящей Политики.",
              "Consent to the processing of personal data may be withdrawn by the User at any time by sending a request to the email address specified in clause 1.2."
            ) }}</p>
          </div>
        </section>

        <section id="conditions" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">06</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Порядок и условия обработки", "Processing conditions") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.1.</span>{{ T(
              "Обработка персональных данных осуществляется с соблюдением принципов и правил, предусмотренных 152-ФЗ, с использованием средств автоматизации и/или без использования таких средств.",
              "Personal data is processed in accordance with the principles and rules set out in 152-FZ, with or without the use of automated means."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.2.</span>{{ T(
              "Оператор осуществляет сбор, запись, систематизацию, накопление, хранение, уточнение (обновление, изменение), извлечение, использование, блокирование, удаление и уничтожение персональных данных.",
              "The Operator performs collection, recording, organisation, accumulation, storage, adaptation (update, modification), retrieval, use, blocking, erasure and destruction of personal data."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.3.</span>{{ T(
              "Хранение персональных данных осуществляется в форме, позволяющей определить субъекта персональных данных, не дольше, чем этого требуют цели их обработки. Персональные данные Пользователя хранятся до момента отзыва Пользователем согласия на их обработку или до достижения целей обработки.",
              "Personal data is stored in a form that permits identification of the data subject for no longer than is necessary for the purposes of processing. The User's personal data is stored until the User withdraws consent or the purposes of processing are achieved."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.4.</span>{{ T(
              "По достижении целей обработки или в случае отзыва Пользователем согласия персональные данные подлежат уничтожению в срок, не превышающий 30 (тридцати) дней с момента поступления соответствующего запроса, если иное не предусмотрено законодательством.",
              "Upon achievement of the processing purposes or withdrawal of consent, personal data shall be destroyed within no more than 30 (thirty) days from receipt of the corresponding request, unless otherwise required by law."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.5.</span>{{ T(
              "Хранение и обработка персональных данных граждан Российской Федерации осуществляются с использованием баз данных, находящихся на территории Российской Федерации, в соответствии с ч. 5 ст. 18 152-ФЗ.",
              "Personal data of Russian Federation citizens is stored and processed using databases located on the territory of the Russian Federation, in accordance with part 5 of article 18 of 152-FZ."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">6.6.</span>{{ T(
              "Оператор не осуществляет трансграничную передачу персональных данных.",
              "The Operator does not carry out cross-border transfers of personal data."
            ) }}</p>
          </div>
        </section>

        <section id="sharing" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">07</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Передача третьим лицам", "Third-party sharing") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">7.1.</span>{{ T(
              "Оператор не передаёт персональные данные Пользователя третьим лицам, за исключением случаев, прямо предусмотренных законодательством Российской Федерации (например, по запросу уполномоченных государственных органов).",
              "The Operator does not share User personal data with third parties except as expressly provided by the laws of the Russian Federation (for example, upon request of authorised state bodies)."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">7.2.</span>{{ T(
              "Оператор вправе привлекать для обработки персональных данных подрядчиков (например, поставщиков услуг хостинга и электронной почты), при условии обеспечения ими конфиденциальности и безопасности персональных данных в соответствии с требованиями 152-ФЗ.",
              "The Operator may engage contractors (such as hosting and email service providers) to process personal data, provided they ensure confidentiality and security in accordance with 152-FZ."
            ) }}</p>
          </div>
        </section>

        <section id="protection" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">08</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Меры по защите персональных данных", "Data protection measures") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">8.1.</span>{{ T(
              "Оператор принимает необходимые правовые, организационные и технические меры для защиты персональных данных от неправомерного или случайного доступа к ним, уничтожения, изменения, блокирования, копирования, предоставления, распространения, а также от иных неправомерных действий в отношении персональных данных.",
              "The Operator takes the legal, organisational and technical measures necessary to protect personal data against unlawful or accidental access, destruction, modification, blocking, copying, provision, dissemination, or any other unlawful actions."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">8.2.</span>{{ T("К таким мерам, в частности, относятся:", "Such measures include, among others:") }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T(
                  "ограничение круга лиц, имеющих доступ к персональным данным;",
                  "restricting the set of persons with access to personal data;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T(
                  "использование защищённого соединения (HTTPS) при передаче данных на Сайте;",
                  "using a secure connection (HTTPS) when transmitting data on the Site;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T(
                  "применение средств антивирусной защиты и защиты от несанкционированного доступа;",
                  "using antivirus and unauthorised-access protection;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T("регулярное резервное копирование данных;", "regular data backups;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <UIcon name="i-heroicons-check-circle" class="size-5 text-primary-500 shrink-0 mt-0.5" />
                <span>{{ T(
                  "своевременное удаление персональных данных, обработка которых не требуется для достижения заявленных целей.",
                  "timely deletion of personal data that is no longer needed for the stated purposes."
                ) }}</span>
              </li>
            </ul>
          </div>
        </section>

        <section id="rights" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">09</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Права Пользователя", "User rights") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">9.1.</span>{{ T("Пользователь имеет право:", "The User has the right to:") }}</p>
            <ul class="space-y-2 pl-1">
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("получать информацию, касающуюся обработки его персональных данных;", "obtain information about the processing of their personal data;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "требовать уточнения своих персональных данных, их блокирования или уничтожения в случае, если они являются неполными, устаревшими, неточными, незаконно полученными или не являются необходимыми для заявленной цели обработки;",
                  "request rectification, blocking or erasure of their personal data where it is incomplete, outdated, inaccurate, unlawfully obtained, or not necessary for the stated purposes of processing;"
                ) }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T("отозвать согласие на обработку персональных данных;", "withdraw consent to processing of their personal data;") }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-2 size-1.5 rounded-full bg-primary-500 shrink-0"></span>
                <span>{{ T(
                  "обжаловать действия или бездействие Оператора в уполномоченный орган по защите прав субъектов персональных данных (Роскомнадзор) или в судебном порядке.",
                  "lodge a complaint against the Operator's actions or inaction with the authorised data protection authority (Roskomnadzor) or through the courts."
                ) }}</span>
              </li>
            </ul>
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">9.2.</span>{{ T(
                "Для реализации своих прав Пользователь направляет Оператору запрос в свободной форме на адрес электронной почты ",
                "To exercise their rights, the User shall send a free-form request to the Operator's email "
              ) }}<strong class="text-gray-900 dark:text-white">structnull@yandex.ru</strong>{{ T(
                ". В запросе необходимо указать сведения, позволяющие идентифицировать Пользователя, и суть обращения.",
                ". The request must include information identifying the User and the subject of the enquiry."
              ) }}
            </p>
          </div>
        </section>

        <section id="cookies" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">10</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Использование файлов cookie", "Use of cookies") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">10.1.</span>{{ T(
              "Сайт может использовать технологию cookie — небольшие текстовые файлы, сохраняемые в браузере Пользователя, — для обеспечения корректной работы Сайта и сохранения пользовательских настроек.",
              "The Site may use cookies — small text files stored in the User's browser — to ensure the Site functions correctly and to remember user preferences."
            ) }}</p>
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">10.2.</span>{{ T(
                "Пользователь вправе самостоятельно отключить сохранение файлов cookie в настройках своего браузера. Отключение может повлиять на работоспособность отдельных функций Сайта. Подробнее см. ",
                "The User may disable cookie storage in their browser settings. Disabling cookies may impact the operation of some Site features. See the "
              ) }}<NuxtLink to="/legal/cookie-policy" class="text-primary-500 hover:text-primary-400 underline underline-offset-2">{{ T("Политику использования файлов cookie", "Cookie Policy") }}</NuxtLink>{{ T(".", " for details.") }}
            </p>
          </div>
        </section>

        <section id="final" class="scroll-mt-24">
          <div class="flex items-center gap-4 mb-5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <span class="flex items-center justify-center size-10 rounded-xl bg-primary-500/10 text-primary-500 font-semibold tabular-nums text-sm shrink-0">11</span>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ T("Заключительные положения", "Final provisions") }}
            </h2>
          </div>
          <div class="space-y-4 text-gray-700 dark:text-gray-300 leading-7">
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">11.1.</span>{{ T(
              "Настоящая Политика является публичным документом и размещается в свободном доступе на Сайте.",
              "This Policy is a public document and is made freely available on the Site."
            ) }}</p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">11.2.</span>{{ T(
              "Оператор вправе вносить изменения в настоящую Политику. Новая редакция Политики вступает в силу с момента её размещения на Сайте, если иное не предусмотрено новой редакцией.",
              "The Operator may amend this Policy. A new version takes effect upon publication on the Site, unless the new version provides otherwise."
            ) }}</p>
            <p>
              <span class="font-semibold text-gray-900 dark:text-white mr-1">11.3.</span>{{ T(
                "Все предложения или вопросы по настоящей Политике следует направлять на адрес электронной почты: ",
                "Suggestions and questions regarding this Policy should be sent to: "
              ) }}<strong class="text-gray-900 dark:text-white">structnull@yandex.ru</strong>.
            </p>
            <p><span class="font-semibold text-gray-900 dark:text-white mr-1">11.4.</span>{{ T(
              "Действующая редакция Политики находится в свободном доступе по адресу: https://dreamteams.luba.skin/",
              "The current version of the Policy is available at: https://dreamteams.luba.skin/"
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
                "По всем вопросам, связанным с обработкой персональных данных, а также для реализации прав, предусмотренных настоящей Политикой.",
                "For any questions about personal data processing or to exercise the rights set out in this Policy."
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
