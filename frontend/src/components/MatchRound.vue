<!-- TODO Pitää tarkistaa patchien ja loadien toimivuus -->

<template>
  <v-card>
    <v-card-title class="pa-0 pl-3 pt-3 pb-3">
      <v-row>
        <v-col cols="2"> Erä {{ props.roundNumber }} </v-col>
        <v-spacer />
        <v-col cols="8" style="text-align: center">
          {{ props.teamName }}
        </v-col>
        <v-col cols="2" style="text-align: right; padding-right: 1em">
          <v-chip
            v-if="!props.showInput && score !== null"
            style="float: right"
            :color="color"
            label
            small
            class="mr-2"
          >
            <strong>{{ score }}</strong>
          </v-chip>
          <v-text-field
            v-else-if="props.showInput"
            v-model="score"
            class="centered-input"
            label="Tulos"
            maxlength="3"
            @input="patchRoundScore(props.teamSide, score)"
          />
        </v-col>
      </v-row>
    </v-card-title>
    <!-- TODO loading -->
    <v-data-table
      v-if="!props.showInput"
      :mobile-breakpoint="0"
      :headers="headersRound"
      :items="props.roundData"
      no-data-text="Ei dataa :("
      :no-filter="true"
      @click:row="handleRedirect"
    >
      <template #bottom></template>
      <!-- This hides the pagination controls-->
    </v-data-table>
    <!-- TODO loading -->
    <v-data-table
      v-else
      v-model="select"
      :mobile-breakpoint="0"
      :headers="headersRound"
      :items="props.roundData"
      :items-per-page="4"
    >
      <template #headers></template>
      <template #item="row">
        <tr>
          <td>
            <v-select
              v-model="selected[row.index].player"
              item-color="red"
              color="red"
              class="text-center pr-1"
              placeholder="Valitse pelaaja"
              :items="props.players"
              item-title="player_name"
              item-value="id"
              single-line
              @update:model-value="(player) => updateThrower(selected[row.index].id, player.id)"
            />
          </td>
          <td v-for="throwString in throwStrings" :key="throwString">
            <v-text-field
              v-model="selected[row.index][getScoreField(throwString)]"
              color="red"
              class="centered-input"
              maxlength="2"
              @input="
                updateThrowScore(getScoreField(throwString), selected[row.index]);
                updateThrowTotal(selected[row.index]);
              "
              @keypress="isNumber($event)"
            />
          </td>
          <td class="centered-input" style="font-size: 18px">
            {{ selected[row.index].score_total }}
          </td>
        </tr>
      </template>
      <template #bottom></template>
      <!-- This hides the pagination controls-->
    </v-data-table>
  </v-card>
</template>

<script setup lang="ts">
  import { ref, Ref } from 'vue';
  import { headersRound } from '@/stores/headers2';
  import { fetchWrapper } from '@/utils/fetchWrapper';

  const throwStrings = ['first', 'second', 'third', 'fourth'] as const;

  type ScoreString = (typeof throwStrings)[number];
  type ScoreField = `score_${ScoreString}`;

  interface RoundPlayer {
    id: string | number;
    player_name: string;
  }

  interface ThrowRow {
    id: string | number;
    player: RoundPlayer | null;
    score_first: string | number | null;
    score_second: string | number | null;
    score_third: string | number | null;
    score_fourth: string | number | null;
    score_total: number;
  }

  interface RoundProps {
    color?: string;
    showInput: boolean;
    roundNumber: '1' | '2';
    roundScore: number;
    roundData: ThrowRow[];
    players: RoundPlayer[];
    teamName: string;
    teamSide: string;
  }

  const props = defineProps<RoundProps>();

  const score: Ref<number | null> = ref(null);
  const select: Ref<ThrowRow[]> = ref([]);
  const selected: Ref<ThrowRow[]> = ref([]);

  const roundIndex = (+props.roundNumber - 1) as 0 | 1;

  const roundScoreUrl = `${import.meta.env.VITE_API_URL}/matches/`;
  const throwUrl = `${import.meta.env.VITE_API_URL}/throws/update/`;

  props.roundData.forEach((item) => {
    if (item.player && Object.keys(item.player).length === 0) {
      item.player = null;
    }
    selected.value.push(item);
  });

  function getScoreField(scoreString: ScoreString): ScoreField {
    return `score_${scoreString}`;
  }

  function handleRedirect(_event: MouseEvent, row: { item: ThrowRow }) {
    if (row.item.player === null) {
      return;
    }
    location.href = `/pelaajat/${row.item.player.id}`;
  }

  /* *
   * This function checks if the key pressed is a number (0-9) or 'H'/'E' (case-insensitive).
   */
  function isNumber(evt: KeyboardEvent) {
    const key = evt.key;
    if (key.length > 1) {
      return; // Allow control keys (Enter, Backspace, etc.)
    }
    if (/^[0-9EeHh]$/.test(key)) {
      return; // Allow numeric keys and 'E', 'H', 'e', 'h'
    }
    evt.preventDefault(); // Prevent any other keys
  }

  function updateThrowTotal(throwerObject: ThrowRow) {
    throwerObject.score_total = 0;

    for (let score of [
      throwerObject.score_first,
      throwerObject.score_second,
      throwerObject.score_third,
      throwerObject.score_fourth,
    ]) {
      let number;
      if (typeof score === 'number') {
        number = score;
      } else if (score === null || score.toLowerCase() === 'h' || score.toLowerCase() === 'e') {
        number = 0;
      } else {
        number = !isNaN(parseInt(score)) ? parseInt(score) : 0;
      }
      throwerObject.score_total += number;
    }
  }

  /*****************/
  /* Update Asyncs */
  /*****************/

  async function patchRoundScore(teamSide: string, roundScore: number | null) {
    const round = ['first', 'second'];

    const splittedUrl = location.href.split('/');
    const idx = splittedUrl[splittedUrl.length - 1];
    const reqUrl = roundScoreUrl + idx;
    fetchWrapper(reqUrl, { [`${teamSide}_${round[roundIndex]}_round_score`]: roundScore }, 'PATCH');
  }

  async function updateThrowScore(throwString: ScoreField, throwObject: ThrowRow) {
    const reqUrl = throwUrl + throwObject.id + '/';
    fetchWrapper(reqUrl, { [throwString]: throwObject[throwString] }, 'PATCH');
  }

  async function updateThrower(
    throwObjectId: string | number,
    playerId: string | number | null | undefined,
  ) {
    if (playerId === undefined) {
      playerId = null;
    }
    const reqUrl = throwUrl + throwObjectId + '/';
    fetchWrapper(reqUrl, { player: playerId }, 'PATCH');
  }
</script>

<style scoped>
  p {
    margin-bottom: 0;
    padding-bottom: 0;
    margin-left: 0.5em;
    font-size: large;
  }

  td {
    padding: 0 !important;
    text-align: center !important;
  }

  .centered-input :deep(input) {
    text-align: center;
  }

  .v-text-field {
    font-size: 1.1em !important;
  }
</style>
