<template>
  <span>
    <v-flex mt-10></v-flex>
    <v-app-bar style="z-index:2;" color="grey darken-3" dark>
      <router-link
        to="/"
        style="text-decoration: none; color:white; padding-right:2em; padding-left:1em;"
      >
        <img src="../../kyykkalogo120px.png">
      </router-link>

      <div v-for="item in headers">
        <v-btn 
          text 
          class="hidden-md-and-down" 
          :to=item.route
          v-if="item.if_clause === undefined && 
          item.title != 'Koti' || item.if_clause"
        >
          {{ item.title }}
        </v-btn>
      </div>

      <v-spacer class="hidden-md-and-down"></v-spacer>
      <v-spacer class="hidden-md-and-down"></v-spacer>
      <v-select
        v-on:input="store.setSeason"
        item-color=red
        v-model="store.setSelectedSeason"
        class="mt-4" align:center
        item-text="name"
        :items="seasons"
      ></v-select>
      <v-spacer class="hidden-md-and-down"></v-spacer>
      <v-spacer class="hidden-md-and-down"></v-spacer>

      <div class="hidden-md-and-down pa-4" v-if="!userStore.loggedIn">
        <!-- <log-in /> -->
      </div>

      <div class="hidden-md-and-down" v-if="!userStore.loggedIn">
        <!-- <register /> -->
      </div>

      <div class="hidden-md-and-down" v-if="userStore.loggedIn">
        <span class="mr-5">{{ store.name }}</span>
        <v-btn 
          class="hidden-md-and-down" 
          v-on:click.native="logout()" 
          :to="'/'"
          >
            Kirjaudu ulos
          </v-btn>
      </div>

      <v-spacer></v-spacer>
      <v-app-bar-nav-icon class="hidden-lg-and-up mr-4" @click.stop="store.drawer = !store.drawer"/>
    </v-app-bar>
      <v-navigation-drawer
        v-model="store.drawer"
        right
        absolute
        temporary
        dark
      >
        <v-list nav>
          <v-list-item-group
            active-class="text--accent-4"
          >
            <div v-for="item in headers">
              <v-list-item :to=item.route v-if="item.if_clause == undefined || item.if_clause">
                <v-list-item-icon>
                  <v-icon>{{ item.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item>
            </div>

            <v-list-item>
              <div class="pa-2">
                <log-in v-if="!userStore.loggedIn" />
                <register v-if="!userStore.loggedIn" />
              </div>
              <v-btn 
                style="position:absolute;"
                v-on:click.native="store.logout()"
                :to="'/'"
                width="95%" 
                v-if="userStore.loggedIn"
              >
                Log out
              </v-btn>
            </v-list-item>
          </v-list-item-group>
        </v-list>
        <template v-if="userStore.loggedIn" v-slot:prepend>
          <v-list-item two-line>
            <v-list-item-avatar>
              <img src="https://www.robertharding.com/watermark.php?type=preview&im=RF/RH_RF/VERTICAL/1112-5071">
            </v-list-item-avatar>

            <v-list-item-content>
              <v-list-item-title>{{ userStore.playerName }}</v-list-item-title>
              <v-list-item-subtitle>Logged In</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </template>
      </v-navigation-drawer>

  </span>
</template>

<script setup>
import { ref } from "vue";
// import LogIn from '@/components/LogIn.vue';
// import Register from '@/components/Register.vue';
import { useNavBarStore } from '../stores/navbar.store';
import { useAuthStore } from '../stores/auth.store';

const store = useNavBarStore();
const userStore = useAuthStore(); 

const drawer = ref(false);

const headers = [ 
  { title: 'Koti', route: '/', icon: 'mdi-home' },
  { title: 'Ottelut', route: '/ottelut', icon: 'mdi-space-invaders' },
  { title: 'Joukkueet', route: '/joukkueet', icon: 'mdi-emoticon-poop' },
  { title: 'Pelaajat', route: '/pelaajat', icon: 'mdi-account-group' },
  { 
    title: 'Oma Joukkue', route: '/joukkue/' + userStore.teamId, 
    if_clause: userStore.loggedIn && userStore.teamId != 'null' && userStore.teamId, 
    icon: 'mdi-account',
  },
  { title: 'Jatkosarja', route: '/jatkosarja', icon: 'mdi-bank' },
  { title: 'SuperWeekend', route: '/superweekend', icon: 'mdi-nuke' },
  { title: 'Info', route: '/info', icon: 'mdi-information-outline' }
];

if (localStorage.seasonId) {
  store.setSelectedSeason(localStorage.seasonId);
}
if (!store.seasons.length) {
  store.getSeasons();
}
</script>

<style>
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
.v-app-bar--fixed {
    position: inherit;
}

.v-select {
  width: 7%;
}
</style>
