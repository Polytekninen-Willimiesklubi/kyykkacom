<template>
  <div class="d-flex flex-column">
    <v-btn
      v-if="authStore.isSuperUser & !newsButton"
      text="Uusi uutinen"
      width="150px"
      class="mb-2"
      @click="newsButton = true"
    />
    <div 
      class="d-flex flex-column"
      v-if="authStore.isSuperUser & newsButton"
    >
      <QuillEditor
        v-model:content="newsStore.newsText"
        :content=newsStore.newsText
        contentType="html" 
        theme="snow" 
        class="mb-1" 
        style="max-width:1140px;"
        toolbar="full"
      />
      <v-text-field 
        label="Otsikko" 
        v-model="newsStore.headline" 
        class="mb-1" 
        width="500px"
      />
      <v-text-field 
        label="Kirjoittaja" 
        v-model="newsStore.writer"
        class="mb-1"
        width="300px"
      />
      <div class="d-flex">
        <v-btn
          text="Peruuta"
          width="100px"
          color="red"
          class="mr-2"
          @click="newsButton = false"
        />
        <v-btn
          text="Julkaise"
          width="100px"
          class="mb-2"
          @click="newsStore.saveNews()"
        />
      </div>
    </div>
    <!-- <h1>Nationaali Kyykkä Liiga</h1> -->
    <div v-for="news in newsStore.currentPageContent">
      <NewsBox
        class="mb-5"
        :writer="news.writer"
        :title="news.header"
        :text="news.text"
        :date="news.date"
      />
    </div>
    <v-card>
      <v-pagination 
        v-if="newsStore.totalPages" 
        variant="outlined" 
        :length="newsStore.totalPages" 
        v-model="newsStore.currentPageNro"
      />
    </v-card>
  </div>
</template>

<script setup>
// TODO move to 'store'
import { useAuthStore } from '@/stores/auth.store';
import { useNewsStore } from '@/stores/news.store';


const authStore = useAuthStore();
const newsStore = useNewsStore();
const newsButton = ref(false);

newsStore.getNews();


</script>