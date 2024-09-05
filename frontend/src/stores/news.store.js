import { getCookie } from '@/stores/auth.store';

const baseUrl = `${import.meta.env.VITE_API_URL}/news/`;

function getDateString() {
    const date = new Date();
    const day = date.getDate();
    let month = date.getMonth() + 1;
    month = Number(month) >= 10 ? month : '0' + month;
    const year = Number(date.getFullYear());
  
    return `${day}.${month}.${year}`;
}

export const useNewsStore = defineStore('news', () => { 
    const allNews = ref([]);
    // Loading data
    const dataReady = ref(false);
    const loading = ref(false);
    const error = ref(false);
    // Saving data
    const saving = ref(false);
    const savingError = ref(false);
    const saved = ref(false);

    // input for saving news
    const newsText = ref('');
    const headline = ref('');
    const writer = ref('');

    // Pagination
    const currentPageNro = ref(1);
    const totalPages = computed(() => {
        return Math.ceil(allNews.value.length / 2)
    })
    const currentPageContent = computed(() => {
        const page = currentPageNro.value
        return [...allNews.value.slice(2*(page-1), 2*page >= allNews.value.length ? undefined : 2*page)]
    })

    async function getNews() {
        loading.value = true;
        error.value = false;
        dataReady.value = false;
        try {
            const response = await fetch(baseUrl, {method: 'GET'});
            
            const payload = await response.json();
            // Sort news recent first
            const kokeileNain = payload.sort((a, b) => {
                return new Date(b.date) - new Date(a.date)
            });
            allNews.value = payload
            dataReady.value = true;

        } catch(e) {
            error.value = true;
            console.log(e)
        } finally {
            loading.value = false;
        }
    }

    async function saveNews() {
        saving.value = true;
        saved.value = false;
        savingError = false;
        try {
            const response = await fetch(baseUrl, {
                'method': 'POST',
                'headers': {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'content-type': 'application/json',
                },
                'body': JSON.stringify({
                    "writer": writer.value,
                    "header": headline.value,
                    "date" : getDateString(),
                    "text" : newsText.value,
                }),
                withCredentials: true,
              });
            if (response.statusText == "ok") {
                saved.value = true;
                writer.value = "";
                newsText.value = "";
                headline.value = "";
            } 
        } catch(e) {
            savingError.value = true;
            console.log(e);
        } finally {
            saving.value = false;
        }
    }

    return {
        allNews,
        dataReady,
        loading,
        error,
        saving,
        savingError,
        saved,
        newsText,
        headline,
        currentPageNro,
        currentPageContent,
        totalPages,
        getNews,
        saveNews,
    }
    
})