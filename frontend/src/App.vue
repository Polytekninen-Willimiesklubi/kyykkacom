<script setup>
// import NavBar from '@/components/NavBar.vue';

// if (!sessionStorage.season_id) {
//   // Index starts at 1 : 2000
//   sessionStorage.season_id = new Date().getFullYear() - 2000 + 1;
// }

</script>


<!-- <template>
  <v-app>
    <v-main>
      <p>
        jotain
      </p>
    </v-main>
  </v-app>
</template> -->

<template>
  <v-app class="app">
    <v-main>
      <p>
        Kokeilu
      </p>
      <router-view />
    </v-main>
  </v-app>
 </template>

<style>

#app {
    background: url('./src/assets/kyykka_background.jpg') no-repeat center center fixed;
    background-size: cover;
    --v-theme-background: rgba(0,0,0,0) !important;
  }
  
.v-application {
  --v-theme-background: rgba(0,0,0,0) !important;
}

</style>
