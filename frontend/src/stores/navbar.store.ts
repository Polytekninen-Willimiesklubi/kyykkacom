import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useTeamsStore } from '@/stores/teams.store';
import { seasonsMappings } from '@/tournament_templates';
import type { Season } from '@/types/api';
import { getLocal, setLocal, setLocalWithRef } from '@/utils/localUtils';
import { fetchWrapper } from '@/utils/fetchWrapper';

const baseUrl = `${import.meta.env.VITE_API_URL}/seasons`;

type SeasonMapping = {
  playoffLines?: number[][];
  second_playofflines?: number[][];
};

export const useNavBarStore = defineStore('navbar', () => {
  const selectedSeason = ref<Season | null>(getLocal('selectedSeason'));
  const seasons = ref<Season[]>(getLocal('allSeasons') || []);
  const loaded = ref<boolean>(true);

  const seasonId = computed<number | undefined>(() => selectedSeason.value?.id);
  const noBrackets = computed<number | undefined>(() => selectedSeason.value?.no_brackets);

  const currentSeasonMapping = computed<SeasonMapping | undefined>(() => {
    const season = selectedSeason.value;
    if (!season?.playoff_format) return undefined;

    // FIXME - this is a temporary fix for season 2024, which has a different playoff format
    // than the rest of the seasons. This should be removed and code should be refactored to
    // handle different playoff formats in a more elegant way.
    const format = season.id === 27 ? 18 : season.playoff_format;
    return (seasonsMappings as Record<number, SeasonMapping>)[format];
  });

  const playoffLines = computed<number[][]>(() => currentSeasonMapping.value?.playoffLines ?? []);
  const secondPlayoffLines = computed<number[][]>(
    () => currentSeasonMapping.value?.second_playofflines ?? [],
  );

  async function setSelectedSeasonById(id: number): Promise<void> {
    const teamStore = useTeamsStore();
    if (seasons.value.length === 0) {
      loaded.value = false;
      await getSeasons();
    }
    selectedSeason.value = seasons.value.find((element: Season) => element.id === id) || null;
    setLocalWithRef('selectedSeason', selectedSeason.value, selectedSeason);
    await teamStore.getTeams();
    loaded.value = true;
  }

  function setSelectedSeason(season: Season): void {
    const teamStore = useTeamsStore();
    selectedSeason.value = season;
    setLocalWithRef('selectedSeason', selectedSeason.value, selectedSeason);
    teamStore.getTeams();
  }

  async function getSeasons(): Promise<void> {
    const teamStore = useTeamsStore();
    try {
      let payload: [Season[], Season] | null = null;
      const allSeasonsTmp: Season[] = getLocal('allSeasons') || [];
      if (!allSeasonsTmp || allSeasonsTmp.length === 0) {
        const tmpPayload = await fetchWrapper(baseUrl, {}, 'GET', true);
        if (tmpPayload !== undefined && tmpPayload !== null) {
          payload = tmpPayload as [Season[], Season];
        }
      }

      if (payload === null) {
        seasons.value = getLocal('allSeasons') || [];
      } else {
        seasons.value = payload[0];
      }

      // Sort seasons to latest year first
      seasons.value.sort((x: Season, y: Season) => {
        if (x.name < y.name) {
          return 1;
        } else if (x.name > y.name) {
          return -1;
        } else {
          return 0;
        }
      });

      setLocal('allSeasons', seasons.value);
      if (payload !== null) {
        setLocalWithRef('selectedSeason', payload[1], selectedSeason);
      }
      // This is async call, but no need to await here
      teamStore.getTeams(seasonId.value);
    } catch (error) {
      console.error(error);
      setLocalWithRef('allSeasons', [], seasons);
      setLocalWithRef('selectedSeason', null, selectedSeason);
    }
  }

  return {
    selectedSeason,
    seasons,
    loaded,
    seasonId,
    noBrackets,
    playoffLines,
    secondPlayoffLines,
    setSelectedSeason,
    setSelectedSeasonById,
    getSeasons,
  };
});
