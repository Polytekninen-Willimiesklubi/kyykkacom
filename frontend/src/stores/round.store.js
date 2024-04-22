import { useAuthStore } from '@/stores/auth.store';
import { getCookie, fetchNewToken } from '@/stores/auth.store';

// const baseUrl = `${import.meta.env.VITE_API_URL}/api/teams/`;
const baseUrl = 'http://localhost:8000/api/matches/'; // TODO: change this to .env variable
const throwUrl = 'http://localhost:8000/api/throws/update/';

export const useRoundStore = defineStore('round', () => {
    const loading = ref(false);

    async function patchRoundScore(teamSide, roundNumber, roundScore) {
        const round = ['first', 'second'];
        const index = roundNumber === '1' ? 0 : 1;
        const key = teamSide + '_' + round[index] + '_round_score'

        const requestOpt = {
            'method': 'PATCH',
            'headers': {
                'X-CSRFToken': getCookie('csrftoken')
            },
            'content-type': 'application/json',
            'body': JSON.stringify({ key : roundScore }),
            withCredentials: true,
        };

        const splittedUrl = location.href.split('/')
        const idx = splittedUrl[splittedUrl.length - 1]
        try {
            const response = await fetch(baseUrl + idx, requestOpt);
            if (!response.ok && response.status === 403) {
                fetchNewToken();
                requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
                const secondResponse = await fetch(baseUrl + idx, requestOpt);
                if (!secondResponse.ok) {
                    console.log("Patch request was denied: " + secondResponse);
                }
            }
        } catch(error) {
            console.log(error)
        }
    }

    /**
     * The function loops through all the column elements of the corresponding row
      and adds them up as total to the last column. The function also updates the database
      accordingly on each runthrough.
     */
    async function updateThrowScores(teamSide, patchData) {
        loading.value = true;
        
        let index

        const post_data =
        {
          score_first: 0,
          score_second: 0,
          score_third: 0,
          score_fourth: 0,
          player: this.$refs['id_' + index].firstChild.data
        }

        const array = [
            'first',
            'second',
            'third',
            'fourth',
        ]

        let throws
        if (this.teamSide == 'home') {
            throws = (this.roundNumber == 1) ? [0, 1, 2, 3] : [8, 9, 10, 11]
        } else if (this.teamSide == 'away') {
            throws = (this.roundNumber == 1) ? [4, 5, 6, 7] : [12, 13, 14, 15]
        }

        array.forEach(function (item) {
            const element = this.$refs[item + '_throw_' + index].$refs.input.value
            let score
            if (element.toLowerCase() == 'h') {
              score = 'h'
            } else if (element.toLowerCase() == 'e') {
              score = 'e'
            } else {
              score = (!isNaN(parseInt(element))) ? parseInt(element) : 0
              total += score
            }
            if (element.length > 0) {
              post_data['score_' + item] = score
            }
        }, this)

        const requestOpt = {
            'method': 'PATCH',
            'headers': {
                'X-CSRFToken': getCookie('csrftoken')
            },
            'content-type': 'application/json',
            'body': JSON.stringify({ key : roundScore }),
            withCredentials: true,
        };

        const splittedUrl = location.href.split('/')
        const idx = splittedUrl[splittedUrl.length - 1]
        try {
            const response = await fetch(throwUrl + idx, requestOpt);
            setTimeout(() => {
                loading.value = false;
            }, 500)

            if (!response.ok && response.status === 403) {
                fetchNewToken();
                requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
                const secondResponse = await fetch(throwUrl + idx, requestOpt);
                if (!secondResponse.ok) {
                    console.log("Patch request was denied: " + secondResponse);
                }
            }
        } catch(error) {
            setTimeout(() => {
                loading.value = false;
            }, 500)
            console.log(error)
        }

    }

    return {
        loading,
        patchRoundScore,
        updateThrowScores
    }
});