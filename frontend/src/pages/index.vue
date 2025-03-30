<template>
  <div class="d-flex flex-column" style="width: 100%;">
    <v-btn
      v-if="authStore.isSuperUser && !newsButton"
      text="Uusi uutinen"
      width="150px"
      class="mb-2"
      @click="newsButton = true"
    />
    <div 
      class="d-flex flex-column"
      v-if="authStore.isSuperUser && newsButton"
    >
      <QuillEditor
        :content="newsStore.newsText"
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
        <div class="success" v-if="newsStore.saved">
          <v-icon
            size="35px"
            icon="mdi-check-box-outline"
            color="green"
          />
          Onnistunut julkaisu!
        </div>
      </div>
    </div>
    <!-- <h1>Nationaali Kyykkä Liiga</h1> -->
    <div v-for="news in newsStore.currentPageContent">
      <NewsBox
        style="width: 100%;"
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
import { useAuthStore } from '@/stores/auth.store';
import { useNewsStore } from '@/stores/news.store';
import { useTeamsStore } from '@/stores/teams.store';


const teamsStore = useTeamsStore();
const authStore = useAuthStore();
const newsStore = useNewsStore();
const newsButton = ref(false);

newsStore.getNews();
teamsStore.getTeams();

</script>
<style scoped>

.success{
  animation: fadeIn 5s;
  visibility: hidden;
}
@keyframes fadeIn {
  0% {opacity: 0; visibility: visible;}
  10% {opacity: 1;}
  100% {opacity: 0; visibility: hidden;}
}

</style>