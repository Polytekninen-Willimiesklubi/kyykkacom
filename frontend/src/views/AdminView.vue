<template>
    <v-layout>
      <v-flex auto>
        <admin></admin>
      </v-flex>
    </v-layout>
  </template>
  
  <script>
  import Admin from '../components/Admin.vue';

  export default {
      name: 'home',
      components: {
        Admin
      }
  };
  </script>
  
  <style>
  </style>
  