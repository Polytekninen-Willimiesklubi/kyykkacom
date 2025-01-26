<template>
  <v-app class="pt-10">
    <NavBar/>
    <v-main class="content">
      <v-layout class="pa-10">
        <router-view class="pr-5"/>
        <Transition name="sidebar">
          <div class="d-flex right align-self-start" v-if="showSidebar">
            <v-tabs-window v-model="tab">
              <v-tabs-window-item value="one">
                <side-bar
                  title="Runkosarja"
                  class="hidden-md-and-down"
                  :headers="headersDefaultSideBar"
                  :sort-by="[
                    (navStore.selectedSeason.playoff_format === 8 ? {key:'first_bracket_placement', order: 'asc'} : {key:'bracket_placement', order: 'asc'}),
                    {key:'points_total', order: 'desc'},
                    {key: 'match_average', order: 'asc'}
                  ]"
                  :teams="teamStore.bracketedTeams"
                  :lines="navStore.playoffLines"
                  :boldingKeys="['P', 'points_total']"
                  :second_stage="false"
                  @close-sidebar="(val) => showSidebar = val"
                >
                  <template #button v-if="navStore.selectedSeason.playoff_format === 8">
                    <v-btn 
                      text="Jatkosarja ->"
                      @click="tab = 'two'"
                    />
                  </template>
                </side-bar>
              </v-tabs-window-item>
              <v-tabs-window-item value="two" v-if = "navStore.selectedSeason.playoff_format === 8">
                <side-bar
                  title="Jatkosarja"
                  class="hidden-md-and-down"
                  :headers="headersDefaultSideBar"
                  :sort-by="[{key:'bracket_placement', order: 'asc'}, {key:'points_total', order: 'desc'}]"
                  :teams="teamStore.secondStageBrackets"
                  :lines="navStore.playoffLines"
                  :boldingKeys="['P', 'points_total']"
                  :second_stage="true"
                >
                  <template #button>
                    <v-btn 
                      text="<- Runkosarja"
                      @click="tab = 'one'"
                    />
                  </template>
                </side-bar>
              </v-tabs-window-item>
            </v-tabs-window>
          </div>
        </Transition>
        <Transition name="openbutton">
          <div v-if="!showSidebar" class="pr-5">
            <v-tooltip
              location="left"
              text="Avaa Sarjataulukko"
            >
              <template #activator="{ props }">
                <v-fab
                  v-bind="props"
                  icon="mdi-format-list-numbered"
                  @click="showSidebar = true"
                />
              </template>
            </v-tooltip>
          </div>
        </Transition>
      </v-layout>
    </v-main>

    <!-- <AppFooter /> -->
  </v-app>
</template>

<script setup>
import { useTeamsStore } from '@/stores/teams.store';
import { useNavBarStore } from '@/stores/navbar.store';
import { headersDefaultSideBar } from '@/stores/headers';

const tab = ref("one");
const showSidebar = ref(true);
const navStore = useNavBarStore(); 
const teamStore = useTeamsStore();

</script>

<style>
.sidebar-enter-active {
  transition: all 1.2s ease-out;
}

.sidebar-leave-active {
  transition: all 0.6s ease-in;
}

.sidebar-enter-from,
.sidebar-leave-to {
  transform: translateX(30vw);
}

.openbutton-enter-active {
  transition: all 1.2s ease-out;
}

.openbutton-leave-active {
  transition: all 0.6s;
}

.openbutton-enter-from,
.openbutton-leave-to {
  transform: translateX(10vw);
}

</style>
