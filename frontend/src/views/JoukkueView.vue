<template>
  <v-layout>
    <v-flex style="width:50%">
      <joukkue />
    </v-flex>
    <v-flex pl-2 class="hidden-md-and-down">
      <side-bar />
    </v-flex>
  </v-layout>
</template>

<script>
import Joukkue from '@/components/Joukkue';
import SideBar from '@/components/SideBar';

export default {
    name: 'joukkueview',
    components: {
        Joukkue,
        SideBar
    }
};
</script>