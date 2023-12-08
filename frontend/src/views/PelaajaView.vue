<template>
    <v-layout>
      <v-flex auto>
        <pelaaja></pelaaja>
      </v-flex>
      <v-flex xs4 class="pl-3 hidden-md-and-down">
        <side-bar></side-bar>
      </v-flex>
    </v-layout>
  </template>


<script>
import SideBar from '@/components/SideBar';
import Pelaaja from '@/components/Pelaaja';

export default {
    name: 'pelaajaview',
    components: {
        Pelaaja,
        SideBar
    }
};
</script>