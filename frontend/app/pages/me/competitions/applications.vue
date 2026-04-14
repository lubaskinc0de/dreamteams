<script setup lang="ts">
const { t } = useI18n();
const router = useRouter();

useSeoMeta({ title: t('applications.title') });
</script>

<template>
  <CompetitionPicker
    :title="t('applications.title')"
    :description="t('applications.selectCompetition')"
    @select="(id: string) => router.push(`/me/competitions/${id}/applications`)"
  />
</template>
