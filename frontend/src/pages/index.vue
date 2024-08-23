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
        v-model:content="newsText"
        :content=newsText
        contentType="html" 
        theme="snow" 
        class="mb-1" 
        style="max-width:1140px;"
        toolbar="full"
      />
      <v-text-field label="Otsikko" v-model="headline" class="mb-1" width="500px"/>
      <v-text-field label="Kirjoittaja" v-model="writer" class="mb-1" width="300px"/>
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
          @click="save()"
        />
      </div>
    </div>
    <!-- <h1>Nationaali Kyykkä Liiga</h1> -->
    <div v-for="news in all_news.slice(2*(newsPage-1), 2*newsPage >= all_news.length ? undefined : 2*newsPage )">
      <NewsBox
        class="mb-5"
        :writer="news.writer"
        :title="news.header"
        :text="news.text"
        :date="news.date"
      />
    </div>
    <v-card>
      <v-pagination variant="outlined" :length="totalNewsPages" v-model="newsPage"/>
    </v-card>
  </div>
</template>

<script setup>
// TODO move to 'store'
import { getCookie } from '@/stores/auth.store';
import { useAuthStore } from '@/stores/auth.store';

const authStore = useAuthStore();
const newsButton = ref(false);

const newsText = ref('');
const headline = ref('');
const writer = ref('');

const newsPage = ref(1);
const totalNewsPages = ref(1);

const response = await fetch("http://localhost:8000/api/news/", {'method': 'GET',});
const payload = await response.json();

const all_news = payload.sort((a, b) => {
  return new Date(b.date) - new Date(a.date)
})

totalNewsPages.value = Math.ceil(all_news.length / 2)
console.log(totalNewsPages.value);
async function save() {
  const date = new Date();
  const day = date.getDate();
  let month = date.getMonth() + 1;
  month = Number(month) >= 10 ? month : '0' + month;
  const year = Number(date.getFullYear());

  const dateString = `${day}.${month}.${year}`;
  const data = {
      "writer": writer.value,
      "header": headline.value,
      "date" : dateString,
      "text" : jotain.value,
  }

  const response = await fetch("http://localhost:8000/api/news/", {
    'method': 'POST',
    'headers': {
        'X-CSRFToken': getCookie('csrftoken'),
        'content-type': 'application/json',
    },
    'body': JSON.stringify(data),
    withCredentials: true,
  });

  writer.value = ""
  newsText.value = ""
  headline.value = ""
  newsButton = false

} 

</script>