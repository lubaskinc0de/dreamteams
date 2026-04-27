<script setup lang="ts">
import type { PreviewCompetitionModel } from "~/types/api";
import { useWindowSize } from "@vueuse/core";

/**
 * Competition Detail Modal/Drawer
 * Desktop: Wide modal with 2-column layout
 * Mobile: Bottom drawer
 */

interface Props {
  competition: PreviewCompetitionModel | null;
  open: boolean;
  canRegister?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  canRegister: true,
});
const emit = defineEmits<{
  close: [];
  register: [id: string];
}>();

const { t } = useI18n();
const {
  formatDateRange,
  formatDateTime,
  formatParticipants,
  formatTeamSize,
  getFormatLabel,
  getParticipantTypeLabel,
} = useCompetitionFormatters();

// Detect mobile (< 768px)
const { width } = useWindowSize();
const isMobile = computed(() => width.value < 768);

// Computed for v-model binding
const isOpen = computed({
  get: () => props.open,
  set: () => emit("close"),
});

const handleRegister = () => {
  if (props.competition) {
    emit("register", props.competition.id);
  }
};
</script>

<template>
  <!-- Desktop: UModal with built-in header/body/footer — body scrolls internally,
       footer stays pinned. Using default (non-scrollable) mode on purpose: the
       theme gives content a fixed max-h and body gets overflow-y-auto, which is
       what keeps long content from bleeding past the footer. -->
  <UModal
    v-if="!isMobile && competition"
    v-model:open="isOpen"
    :close="{ size: 'xl' }"
    :ui="{
      content: 'sm:max-w-5xl',
      header: 'items-start p-4 sm:p-6 lg:p-8',
      body: 'p-4 sm:p-6 lg:p-8',
      footer: 'justify-center p-4 sm:p-6 lg:p-8',
    }"
  >
    <template #header>
      <div class="flex-1 min-w-0 pr-8">
        <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white leading-tight mb-4">
          {{ competition.title }}
        </h2>
        <CompetitionDomainBadges :domains="competition.domains" size="md" />
      </div>
    </template>

    <template #body>
      <div class="space-y-8">
        <!-- Description -->
        <section>
          <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
            {{ t("competitionsPreview.detail.description") }}
          </h3>
          <p class="text-base text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
            {{ competition.description }}
          </p>
        </section>

        <div class="border-t border-gray-200 dark:border-gray-700" />

        <!-- 2-Column Grid for Details -->
        <div class="grid md:grid-cols-2 gap-8">
          <!-- Left Column: Schedule & Participants -->
          <div class="space-y-8">
            <!-- Schedule -->
            <section>
              <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
                {{ t("competitionsPreview.detail.schedule") }}
              </h3>
              <div class="space-y-4">
                <div class="flex items-start gap-3">
                  <UIcon name="i-heroicons-calendar" class="size-6 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {{ t('competitionsPreview.detail.registration') }}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ formatDateRange(competition.schedule.registration_start, competition.schedule.registration_end) }}
                    </p>
                  </div>
                </div>
                <div
                  v-if="competition.schedule.team_formation_start && competition.schedule.team_formation_end"
                  class="flex items-start gap-3"
                >
                  <UIcon name="i-heroicons-user-group" class="size-6 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {{ t('competitionsPreview.detail.teamFormation') }}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ formatDateRange(competition.schedule.team_formation_start, competition.schedule.team_formation_end) }}
                    </p>
                  </div>
                </div>
              </div>
            </section>

            <!-- Participants -->
            <section>
              <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
                {{ t("competitionsPreview.detail.participants") }}
              </h3>
              <div class="space-y-4">
                <div class="flex items-start gap-3">
                  <UIcon name="i-heroicons-users" class="size-6 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {{ t('competitionsPreview.card.participants') }}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ formatParticipants(competition.members_count, competition.participant_limits.max) }}
                    </p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <UIcon name="i-heroicons-academic-cap" class="size-6 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {{ t('competitionsPreview.detail.participantType') }}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ getParticipantTypeLabel(competition.participant_type) }}
                    </p>
                  </div>
                </div>
                <div
                  v-if="competition.team_size"
                  class="flex items-start gap-3"
                >
                  <UIcon name="i-heroicons-user-group" class="size-6 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {{ t('competitionsPreview.detail.teamSize') }}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ formatTeamSize(competition.team_size) }}
                    </p>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <!-- Right Column: Venue & Organizer -->
          <div class="space-y-8">
            <!-- Venue -->
            <section>
              <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
                {{ t("competitionsPreview.detail.venue") }}
              </h3>
              <div class="space-y-4">
                <div class="flex items-start gap-3">
                  <UIcon name="i-heroicons-map-pin" class="size-6 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {{ t('competition.form.venue.format.label') }}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ getFormatLabel(competition.venue.format) }}
                    </p>
                  </div>
                </div>
                <div v-if="competition.venue.location" class="flex items-start gap-3">
                  <UIcon name="i-heroicons-building-office-2" class="size-6 text-primary-500 mt-0.5 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                      {{ t('competition.form.venue.location.label') }}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400 break-words">
                      {{ competition.venue.location }}
                    </p>
                  </div>
                </div>
              </div>
            </section>

            <!-- Organizer -->
            <section>
              <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
                {{ t("competitionsPreview.detail.organizer") }}
              </h3>
              <div class="flex items-center gap-4 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                <UAvatar
                  :src="competition.organizer.avatar_url || '/no-photo.png'"
                  :alt="competition.organizer.name"
                  size="lg"
                />
                <div>
                  <p class="font-semibold text-gray-900 dark:text-white text-base">
                    {{ competition.organizer.name }}
                  </p>
                </div>
              </div>
            </section>
          </div>
        </div>

        <!-- Milestones (Full Width) -->
        <section v-if="competition.milestones.length > 0">
          <div class="border-t border-gray-200 dark:border-gray-700 mb-6" />
          <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-6">
            {{ t("competitionsPreview.detail.milestones") }}
          </h3>
          <UTimeline
            :items="competition.milestones.map((milestone) => ({
              date: formatDateTime(milestone.timestamp),
              title: milestone.title,
              description: milestone.description ?? undefined,
              icon: 'i-heroicons-flag',
            }))"
            color="primary"
          />
        </section>
      </div>
    </template>

    <template v-if="canRegister" #footer>
      <UButton
        :label="t('competitionsPreview.detail.registerButton')"
        icon="i-heroicons-bolt"
        trailing
        color="primary"
        size="lg"
        class="w-full sm:w-auto justify-center"
        @click="handleRegister"
      />
    </template>
  </UModal>

  <!-- Mobile: Bottom Drawer -->
  <UDrawer
    v-else-if="competition"
    v-model:open="isOpen"
    direction="bottom"
  >
    <template #header>
      <div class="w-full space-y-3">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white leading-tight">
          {{ competition.title }}
        </h2>
        <CompetitionDomainBadges :domains="competition.domains" size="sm" />
      </div>
    </template>

    <template #body>
      <div class="space-y-6 pb-4">
        <!-- Description -->
        <section>
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
            {{ t("competitionsPreview.detail.description") }}
          </h3>
          <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
            {{ competition.description }}
          </p>
        </section>

        <div class="border-t border-gray-200 dark:border-gray-700" />

        <!-- Schedule -->
        <section>
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
            {{ t("competitionsPreview.detail.schedule") }}
          </h3>
          <div class="space-y-3">
            <div class="flex items-start gap-3">
              <UIcon name="i-heroicons-calendar" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium text-gray-900 dark:text-white mb-1">
                  {{ t('competitionsPreview.detail.registration') }}
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  {{ formatDateRange(competition.schedule.registration_start, competition.schedule.registration_end) }}
                </p>
              </div>
            </div>
            <div
              v-if="competition.schedule.team_formation_start && competition.schedule.team_formation_end"
              class="flex items-start gap-3"
            >
              <UIcon name="i-heroicons-user-group" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium text-gray-900 dark:text-white mb-1">
                  {{ t('competitionsPreview.detail.teamFormation') }}
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  {{ formatDateRange(competition.schedule.team_formation_start, competition.schedule.team_formation_end) }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <div class="border-t border-gray-200 dark:border-gray-700" />

        <!-- Participants & Venue -->
        <div class="space-y-6">
          <section>
            <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
              {{ t("competitionsPreview.detail.participants") }}
            </h3>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <UIcon name="i-heroicons-users" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-gray-900 dark:text-white mb-1">
                    {{ t('competitionsPreview.card.participants') }}
                  </p>
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    {{ formatParticipants(competition.members_count, competition.participant_limits.max) }}
                  </p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <UIcon name="i-heroicons-academic-cap" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-gray-900 dark:text-white mb-1">
                    {{ t('competitionsPreview.detail.participantType') }}
                  </p>
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    {{ getParticipantTypeLabel(competition.participant_type) }}
                  </p>
                </div>
              </div>
              <div
                v-if="competition.team_size"
                class="flex items-start gap-3"
              >
                <UIcon name="i-heroicons-user-group" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-gray-900 dark:text-white mb-1">
                    {{ t('competitionsPreview.detail.teamSize') }}
                  </p>
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    {{ formatTeamSize(competition.team_size) }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
              {{ t("competitionsPreview.detail.venue") }}
            </h3>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <UIcon name="i-heroicons-map-pin" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-gray-900 dark:text-white mb-1">
                    {{ t('competition.form.venue.format.label') }}
                  </p>
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    {{ getFormatLabel(competition.venue.format) }}
                  </p>
                </div>
              </div>
              <div v-if="competition.venue.location" class="flex items-start gap-3">
                <UIcon name="i-heroicons-building-office-2" class="size-5 text-primary-500 mt-0.5 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-gray-900 dark:text-white mb-1">
                    {{ t('competition.form.venue.location.label') }}
                  </p>
                  <p class="text-xs text-gray-600 dark:text-gray-400 break-words">
                    {{ competition.venue.location }}
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Milestones -->
        <section v-if="competition.milestones.length > 0">
          <div class="border-t border-gray-200 dark:border-gray-700 mb-6" />
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
            {{ t("competitionsPreview.detail.milestones") }}
          </h3>
          <UTimeline
            :items="competition.milestones.map((milestone) => ({
              date: formatDateTime(milestone.timestamp),
              title: milestone.title,
              description: milestone.description ?? undefined,
              icon: 'i-heroicons-flag',
            }))"
            color="primary"
            size="sm"
          />
        </section>

        <!-- Organizer -->
        <section>
          <div class="border-t border-gray-200 dark:border-gray-700 mb-6" />
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
            {{ t("competitionsPreview.detail.organizer") }}
          </h3>
          <div class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
            <UAvatar
              :src="competition.organizer.avatar_url || '/no-photo.png'"
              :alt="competition.organizer.name"
              size="md"
            />
            <div>
              <p class="font-semibold text-gray-900 dark:text-white text-sm">
                {{ competition.organizer.name }}
              </p>
            </div>
          </div>
        </section>
      </div>
    </template>

    <template v-if="canRegister" #footer>
      <div class="flex justify-center">
        <UButton
          :label="t('competitionsPreview.detail.registerButton')"
          icon="i-heroicons-bolt"
          trailing
          color="primary"
          size="md"
          class="w-full justify-center"
          @click="handleRegister"
        />
      </div>
    </template>
  </UDrawer>
</template>
