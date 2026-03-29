<template>
  <div class="flex-1-1-100">
    <v-card>
      <v-card-title>
        Joukkueet
        <v-row>
          <v-col cols="4">
            <v-text-field v-model="search" color="red" label="Etsi" single-line />
          </v-col>
          <v-spacer />
        </v-row>
      </v-card-title>
      <v-data-table
        :mobile-breakpoint="0"
        density="compact"
        color="alert"
        :headers="headersTeams"
        :search="search"
        :items="teamStore.allTeams"
        :loading="teamStore.loading"
        no-data-text="Ei dataa :("
        items-per-page="-1"
        @click:row="handleRedirect"
      >
        <template #item.current_name="{ item }">
          <v-row>
            <v-spacer />
            <v-col cols="9">
              <span>{{ item.current_name }}</span>
            </v-col>
            <v-col>
              <v-row class="justify-start">
                <template v-for="(accolade, i) in teamStore.seasonTeamAccolades[item.id]" :key="i">
                  <v-col cols="3">
                    <accolade-icon :filename="accolade.icon">
                      <v-tooltip
                        activator="parent"
                        :text="accolade?.name + ' ' + accolade.placement + '. Sija'"
                        location="right"
                      />
                    </accolade-icon>
                  </v-col>
                </template>
                <v-spacer />
              </v-row>
            </v-col>
          </v-row>
        </template>
        <template #bottom />
      </v-data-table>
    </v-card>
  </div>
</template>

<route lang="yaml">
meta:
  layout: 'withoutSidebar'
</route>

<script setup lang="ts">
  import { useTeamsStore } from '@/stores/teams.store';
  import { headersTeams } from '@/stores/headers2';
  import { ref } from 'vue';

  const teamStore = useTeamsStore();
  
  type TeamRow = (typeof teamStore.allTeams)[number];

  const search = ref<string>('');

  function handleRedirect(_event: MouseEvent, row: { item: TeamRow }) {
    location.href = '/joukkueet/' + row.item.team_id;
  }
</script>
