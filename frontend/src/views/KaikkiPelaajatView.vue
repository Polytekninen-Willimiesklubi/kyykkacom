<template>
    <v-layout>
      <v-flex auto>
        <kaikki-pelaajat />
      </v-flex>
      <v-flex xs4 class="pl-3 hidden-md-and-down">
        <side-bar />
      </v-flex>
    </v-layout>
  </template>


<script>
import SideBar from '@/components/SideBar';
import KaikkiPelaajat from '@/components/KaikkiPelaajat';

export default {
    name: 'kaikkipelaajatview',
    components: {
        KaikkiPelaajat,
        SideBar
    }
};
</script>