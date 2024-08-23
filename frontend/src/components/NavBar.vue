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
        :to="item.route"
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
              <v-btn block variant="text" text="yleisiä ohjeita" to="/"/>
            </v-list-item>
            <v-list-item>
              <v-btn block variant="text" text="säännöt" to="/"/>
            </v-list-item>
            <v-list-item>
              <v-btn block variant="text" text="hall-of-fame" to="/"/>
            </v-list-item>
            <v-list-item>
              <v-btn block variant="text" text="Muualla kyykkää" to="/"/>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
      <v-btn 
        class="hidden-md-and-down"
        :text="item.title"
        :to=item.route
        v-else-if="item.if_clause === undefined && 
        item.title != 'Koti' || item.if_clause"
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
    </div>

    <div class="hidden-md-and-down" v-if="!userStore.loggedIn">
      <register />
    </div>

    <div class="hidden-md-and-down" v-if="userStore.loggedIn">
      <span class="mr-5">{{ userStore.playerName }}</span>
      <v-btn 
        class="hidden-md-and-down"
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
      location="right"
      absolute
      temporary
      dark
    >
      <v-list :nav="true">
        <template v-for="item in headersNavBar">
          <v-list-item 
            :to=item.route v-if="item.if_clause == undefined || item.if_clause"
            :prepend-icon="item.icon"
            :title="item.title"  
          />
        </template>

        <v-list-item>
          <div class="pa-2" v-if="!userStore.loggedIn">
            <log-in />
            <register />
          </div>
          <v-btn v-else
            text="Log out"
            style="position:absolute;"
            @click="userStore.logOut()"
            :to="'/'"
            width="95%"
          />
        </v-list-item>
      </v-list>
      <template v-if="userStore.loggedIn" v-slot:prepend>
        <v-list-item 
          :title="userStore.playerName"
          subtitle="Logged In"
          two-line
        >
          <v-avatar
            image="https://www.robertharding.com/watermark.php?type=preview&im=RF/RH_RF/VERTICAL/1112-5071"
          />
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

// to Header add if-clause and id to the route
let header = headersNavBar
header[4]["if_clause"] = userStore.loggedIn && userStore.teamId != 'null' && userStore.teamId
header[4]["route"] +=  userStore.teamId

if (!navStore.seasons.length) {
  navStore.getSeasons();
}
</script>

<style>
.v-toolbar__content {
  overflow: visible !important;
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
