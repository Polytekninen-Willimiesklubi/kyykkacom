<template>
    <VuePdfEmbed 
        source="saannot_2024.pdf" 
        download="saannot_2024.pdf"
    />
</template>

<route lang="yaml">
    meta:
        layout: "withoutSidebar"
</route>

<script setup>
import VuePdfEmbed from 'vue-pdf-embed';

</script>

<style>
.rules__link {
  text-decoration: none;
  color: red !important;
}

</style>