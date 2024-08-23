<template>
  <v-row>
    <v-col>
      <span v-if="showAllPages">
          {{ pageCount }} sivu(a)
      </span>
      <span v-else>
        <button :disabled="page <= 1" @click="page--">❮</button>
  
        {{ page }} / {{ pageCount }}
  
        <button :disabled="page >= pageCount" @click="page++">❯</button>
      </span>
    </v-col>
    <v-col>
      <label >
        <input 
          v-model="showAllPages"
          type="checkbox"
          @input="() => {page = showAllPages ? null : 1}"
        >
        Näytä kaikki sivut
      </label>
    </v-col>
  </v-row>
  <v-row>
    <v-col align="center">
      <VuePdfEmbed 
        source="saannot_2024.pdf" 
        download="saannot_2024.pdf"
        :page="page"
        @loaded="(obj) => {pageCount = obj.numPages; page = 1;console.log(pageCount)}"
      />
    </v-col>
  </v-row>
</template>

<script setup>
import VuePdfEmbed from 'vue-pdf-embed';

const pageCount = ref(null);
const page = ref(null);
const showAllPages = ref(false);

</script>

<style>
.rules__link {
  text-decoration: none;
  color: red !important;
}

</style>
