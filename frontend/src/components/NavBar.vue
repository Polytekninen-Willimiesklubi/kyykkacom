<template>
  <v-app-bar
    style="z-index:2;" 
    color="grey-darken-3"
  >
    <router-link
      to="/"
      style="text-decoration: none;
       color:white; 
       padding-right:2em; 
       padding-left:2em;
      "
    >
      <img src="@/assets/kyykkalogo120px.png">
    </router-link>

    <template v-for="item in headersNavBar">
      
      <v-btn
        v-if="item.title === 'Info'"
        class="hidden-md-and-down"
        append-icon="mdi-menu-down"
      >
        {{ item.title }}
        <v-menu
          activator="parent"
          :open-on-hover="true"
          color="grey-darken-3"
        >
          <v-list bg-color="grey-darken-3">
            <v-list-item>
              <v-btn block variant="text" text="yleisiä ohjeita" to="/info/yleista"/>
            </v-list-item>
            <v-list-item>
              <v-btn block variant="text" text="säännöt" to="/info/saannot"/>
            </v-list-item>
            <v-list-item>
              <v-btn block variant="text" text="hall-of-fame" to="/info/hof"/>
            </v-list-item>
            <v-list-item>
              <v-btn block variant="text" text="Muualla kyykkää" to="/info/links"/>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
      <v-btn
        v-else-if="item.title === 'Pelaajat' || item.title === 'Joukkueet'"
        class="hidden-md-and-down"
        append-icon="mdi-menu-down"
        :to="item.route"
      >
        {{ item.title }}
        <v-menu
          activator="parent"
          :open-on-hover="true"
          color="grey-darken-3"
        >
          <v-list bg-color="grey-darken-3">
            <v-list-item>
              <v-btn block variant="text" text="Valittu kausi" :to="item.route"/>
            </v-list-item>
            <v-list-item>
              <v-btn block variant="text" text="Kaikki kaudet" :to="item.route + '/kaikki'"/>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
      <v-btn 
        class="hidden-md-and-down"
        :text="item.title"
        :to="item.route"
        v-else-if="
        item.if_clause === undefined 
        && item.title !== 'Koti'
        && item.title !== 'Oma Joukkue'
        && item.title !== 'Runkosarja'
        || item.if_clause"
      />
    </template>

    <v-spacer class="hidden-md-and-down" />
    <v-spacer class="hidden-md-and-down" />
    <v-select
      @update:model-value="(val) => navStore.setSelectedSeason(val)"
      v-model="navStore.selectedSeason"
      :items="navStore.seasons"
      class="mt-4"
      item-title="name"
      item-color="red"
      return-object
      attach
    />
    <v-spacer class="hidden-md-and-down" />
    <v-spacer class="hidden-md-and-down" />

    <div class="hidden-md-and-down pa-4" v-if="!userStore.loggedIn">
      <log-in />
      <register />
    </div>

    <div class="hidden-md-and-down" v-else>
      <v-btn v-if="userStore.teamId"
        text="Oma Joukkue"
        :to="{ path: `/joukkueet/${userStore.teamId}`}"
      />
      <v-btn v-else
        text="Ei joukkuetta"
      />
      <v-btn
        :text="userStore.playerName"
        :to="'/pelaajat/' + userStore.userId" 
      />
      <v-btn
        text="Kirjaudu Ulos"
        @click="userStore.logOut()" 
        :to="'/'"
      />
    </div>

    <v-spacer />
    <v-app-bar-nav-icon class="hidden-lg-and-up mr-4" @click.stop="drawer = !drawer"/>
  </v-app-bar>
  <v-navigation-drawer
    v-model="drawer"
    :location="$vuetify.display.mobile ? 'right' : undefined"
    temporary
  >
    <v-list :nav="true">

      <template v-for="item in headersNavBar">
        <v-list-item v-if="(item.title !== 'Oma Joukkue' || userStore.teamId) && item.title !== 'Info'"
          :to="item.title !== 'Oma Joukkue' ? item.route : item.route + userStore.teamId" 
          :prepend-icon="item.icon"
          :title="item.title"
        />
      </template>
      <v-list-item
        to="/joukkueet/kaikki"
        prepend-icon="mdi-format-list-bulleted-type"
        title="Kaikkien kausien joukkueet"
      />
      <v-list-item
        to="/pelaajat/kaikki"
        prepend-icon="mdi-format-list-bulleted-type"
        title="Kaikkien kausien pelaajat"
      />
      <v-list-item
        to="/info/yleista"
        prepend-icon="mdi-information-outline"
        title="Yleisiä ohjeita"
      />
      <v-list-item
        to="/info/saannot"
        prepend-icon="mdi-book-open-variant"
        title="Säännöt"
      />
      <v-list-item
        to="/info/hof"
        prepend-icon="mdi-trophy-variant"
        title="Hall of Fame"
      />
      <v-list-item
        to="/info/links"
        prepend-icon="mdi-link-variant"
        title="Muualla kyykkää"
      />

      <v-list-item>
        <div class="pa-2" v-if="!userStore.loggedIn">
          <log-in />
          <register />
        </div>
        <v-btn v-else
          text="Kirjaudu ulos"
          style="position:absolute;"
          @click="userStore.logOut()"
          :to="'/'"
          width="95%"
        />
      </v-list-item>

    </v-list>
    <template #prepend v-if="userStore.loggedIn">
      <v-list-item>
        <v-row align="center" style="padding-top: 4px;">
          <v-col cols="4">
            <v-avatar
              image="https://www.robertharding.com/watermark.php?type=preview&im=RF/RH_RF/VERTICAL/1112-5071"
            />
          </v-col>
          <v-col>
            {{ userStore.playerName }}
          </v-col>
        </v-row>
      </v-list-item>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { useNavBarStore } from '../stores/navbar.store';
import { useAuthStore } from '../stores/auth.store';
import { headersNavBar } from '@/stores/headers';


const navStore = useNavBarStore();
const userStore = useAuthStore();

const drawer = ref(false);

if (navStore.seasons && !navStore.seasons.length) {
  navStore.getSeasons();
}
</script>

<style>
.v-toolbar__content {
  overflow: visible !important;
}

body {
  overflow: hidden;
}

a {
  color: red;
  text-decoration: none;
  font-size: 130%;
}

.v-data-table-header th {
  white-space: nowrap;
}
</style>

<style scoped>

.v-select {
  width: 7%;
}
</style>
