import { getCookie } from '@/stores/auth.store';

const baseUrl = `${import.meta.env.VITE_API_URL}/news/`;

function getDateString() {
    const date = new Date(Date.now());
    return date.toISOString();
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
    const noNewsPerPage = 5;
    const currentPageNro = ref(1);
    const totalPages = computed(() => {
        return Math.ceil(allNews.value.length / noNewsPerPage);
    })
    const currentPageContent = computed(() => {
        const page = currentPageNro.value;
        return [...allNews.value.slice(noNewsPerPage * (page - 1), noNewsPerPage * page >= allNews.value.length ? undefined : noNewsPerPage * page)];
    })

    async function getNews() {
        loading.value = true;
        error.value = false;
        dataReady.value = false;
        try {
            const response = await fetch(baseUrl, { method: 'GET' });

            const payload = await response.json();
            // Sort news recent first
            allNews.value = payload.sort((a, b) => {
                return new Date(b.date) - new Date(a.date);
            });
            dataReady.value = true;

        } catch (e) {
            error.value = true;
            console.log(e);
        } finally {
            loading.value = false;
        }
    }

    async function saveNews() {
        saving.value = true;
        saved.value = false;
        savingError.value = false;
        try {
            const response = await fetch(baseUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'content-type': 'application/json',
                },
                body: JSON.stringify({
                    "writer": writer.value,
                    "header": headline.value,
                    "date": getDateString(),
                    "text": newsText.value,
                }),
                credentials: 'include',
            });
            console.log(response.status);
            if (response.status === 200) {
                saved.value = true;
                writer.value = "";
                newsText.value = "";
                headline.value = "";
                getNews();
            }
        } catch (e) {
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
        writer,
        currentPageNro,
        currentPageContent,
        totalPages,
        getNews,
        saveNews,
    }

})