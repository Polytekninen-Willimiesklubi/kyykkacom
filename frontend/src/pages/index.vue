<template>
  <div class="d-flex flex-column">
    <!-- <h1>Nationaali Kyykkä Liiga</h1> -->
    <div class="d-flex">
      <!-- <Editor v-model="jotain" editor-style="height: 1000 px">
        <template v-slot:toolbar>
            <span class="ql-formats">
                <button v-tooltip.bottom="'Bold'" class="ql-bold"></button>
                <button v-tooltip.bottom="'Italic'" class="ql-italic"></button>
                <button v-tooltip.bottom="'Underline'" class="ql-underline"></button>
            </span>
        </template>
      </Editor> -->
    </div>
    <div v-for="news in all_news">
      <NewsBox
        class="mb-5"
        :writer="news.kirjoittaja"
        :title="news.otsikko"
        :text="news.text"
        :pvm="news.pvm"
      />
    </div>
  </div>
</template>

<script setup>
import all_news from '@/news'

const jotain = ref('')


</script>
