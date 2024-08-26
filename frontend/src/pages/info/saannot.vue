<template>
    <v-card class="mr-5" style="width: '900px';">
        <VuePdfEmbed 
            source="/saannot_2024.pdf" 
            download="/saannot_2024.pdf"
            width="900"
            text-layer
            :page="page"
            @loaded="(obj) => {pageCount = obj.numPages; page = null;}"
        />
    </v-card>
</template>
<!-- 
<route lang="yaml">
    meta:
        layout: "withoutSidebar"
</route> -->

<script setup>
import VuePdfEmbed from 'vue-pdf-embed';
import 'vue-pdf-embed/dist/styles/textLayer.css'

const pageCount = ref(null);
const page = ref(null);

</script>

<style>
.rules__link {
  text-decoration: none;
  color: red !important;
}

</style>