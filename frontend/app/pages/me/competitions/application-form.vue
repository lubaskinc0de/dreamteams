<script setup lang="ts">
const { t } = useI18n();
const router = useRouter();

useSeoMeta({ title: t('applicationForm.title') });
</script>

<template>
  <CompetitionPicker
    :title="t('applicationForm.title')"
    :description="t('applicationForm.selectCompetition')"
    @select="(id: string) => router.push(`/me/competitions/${id}/application-form`)"
  />
</template>
