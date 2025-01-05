import { getCookie, fetchNewToken } from '@/stores/auth.store';

const roundScoreUrl = `${import.meta.env.VITE_API_URL}/matches/`;
const throwUrl = `${import.meta.env.VITE_API_URL}/throws/update/`;

async function patchRequest(data, reqUrl) {
  const requestOpt = {
    'method': 'PATCH',
    'headers': {
        'X-CSRFToken': getCookie('csrftoken'),
        'content-type': 'application/json',
    },
    'body': JSON.stringify(data),
    withCredentials: true,
  };
  try {
      const response = await fetch(reqUrl, requestOpt);
      if (!response.ok && response.status === 403) {
          fetchNewToken();
          requestOpt.headers['X-CSRFToken'] = getCookie('csrftoken');
          const secondResponse = await fetch(reqUrl, requestOpt);
          if (!secondResponse.ok) {
              console.log("Patch request was denied: " + secondResponse);
          }
      }
  } catch(error) {
      console.log(error)
  }
} 

export const useRoundStore = defineStore('round', () => {
    async function patchRoundScore(teamSide, roundNumber, roundScore) {
      const round = ['first', 'second'];
      const index = roundNumber === '1' ? 0 : 1;
      
      const splittedUrl = location.href.split('/');
      const idx = splittedUrl[splittedUrl.length - 1];
      const reqUrl = roundScoreUrl + idx
      patchRequest({[`${teamSide}_${round[index]}_round_score`]: roundScore}, reqUrl);
    }

    async function updateThrowScore(throwString, throwObject) {
      const reqUrl = throwUrl + throwObject.id + "/"
      patchRequest({[throwString]: throwObject[throwString]}, reqUrl)
    }

    async function updateThrower(throwObject) {
      const reqUrl = throwUrl + throwObject.id + "/"
      patchRequest({"player": throwObject.player.id}, reqUrl)
    }

    return {
        patchRoundScore,
        updateThrowScore,
        updateThrower
    }
});