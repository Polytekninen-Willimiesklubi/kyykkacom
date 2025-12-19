<!-- Only removes the sidebar. Sidebar is reused as differently in 
  these pages and shoud be rendered in the "page"- file -->
<template>
  <v-app class="pt-10">
    <NavBar/>
    <v-main class="content">
      <v-layout class="pa-10 centered">
        <router-view />
      </v-layout>
    </v-main>

    <!-- <AppFooter /> -->
  </v-app>
</template>

<style scoped>

.centered {
  justify-content: center;
}

</style>