<template>
  <v-card>
    <v-card-title>
      <v-row>
        <v-col cols="6">{{ props.title }}</v-col>
        <v-col cols="5" align="right"><slot name="button"></slot></v-col>
        <v-col cols="1" align="right" class="close_button" v-if="!disable_close">
          <v-tooltip
            location="top"
            text="Piilota Taulukko"
          >
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                size="small"
                color="blue-grey-lighten-2"
                icon="mdi-window-minimize"
                density="compact"
                @click="$emit('closeSidebar', false)"
                rounded
              />
            </template>
          </v-tooltip>
        </v-col>
      </v-row>
    </v-card-title>
    <v-row v-for="(listItem, index) in teams" :key="index">
      <v-col>
        <v-card-subtitle v-if="props.teams.length > 1">
          <b v-if="!props.second_stage">Lohko {{ String.fromCharCode(65+index) }}</b>
          <b v-else>{{ secondStageNames[index] }} Lohko</b>
        </v-card-subtitle>
        <v-divider />
        <v-data-table
          :mobile-breakpoint=0
          class="sidebar"
          :headers="headers"
          :items="listItem"
          :sort-by="sortBy"
          no-data-text="Ei dataa :("
          items-per-page="-1"
          density="compact"
        >
          <!-- Tooltip and header bolding -->
          <template #headers="{ columns }">
            <tr>
              <template v-for="column in columns" :key="column.key">
                <th class="v-data-table__td v-data-table__th">
                  <div class="v-data-table-header__content">
                    <span :style="boldingKeys && 
                      column.title === boldingKeys[0] ? 'font-weight:bold' : ''"
                    >
                      {{ column.title }}
                    </span>
                  </div>
                  <v-tooltip v-if="column.tooltip !== undefined"
                    activator="parent"
                    location="bottom"
                    :text="column.tooltip"
                  />
                </th>
              </template>
            </tr>
          </template>
          <!-- Bolding and line drawing -->
          <template #item = "{ item, index }">
            <tr
              class="v-data-table__tr v-data-table__tr"
              :class="{'first-border': isFirst(index), 
                'second-border': isSecond(index)}"
              @click="handleRedirect(item['id'])"
            >
              <td 
                v-for="header in headers"
                :style="boldingKeys && header.key === boldingKeys[1] 
                  ? 'font-weight:bold' :''"
              >
                {{ item[header.key] }}
              </td>
            </tr>
          </template>
          <template #bottom></template> <!-- This disables paginations menu -->
        </v-data-table>
      </v-col>
    </v-row>
    <v-divider v-if="props.teams.length > 1" />
  </v-card>
</template>

<script setup>
const secondStageNames = ["Ylempi", "Keskimmäinen", "Alempi"];
const props = defineProps({
  title: String,
  headers: Array,
  teams: Array,
  sortBy: Array,
  lines: Array,
  boldingKeys: Array,
  second_stage: Boolean,
  disable_close: {
    type: Boolean,
    default: false,
  },
})

function handleRedirect(index) {
  location.href = '/joukkueet/' + index
}
function isFirst(val) {
  if (props.lines.length === 0) return false;
  const index = props.teams.length > 1 ? 1 : 0;
  return props.lines && props.lines.length > 1 && props.lines[index][0] === val+1
}
function isSecond(val) {
  if (props.lines.length === 0) return false;
  const index = props.teams.length > 1 ? 1 : 0;
  return props.lines && props.lines.length === 1 && props.lines[index][0] === val+1 ||
        props.lines.length === 2 && props.lines[index][1] === val+1
}

</script>

<style scoped>

.first-border {
  border-bottom: 0.15rem dashed red !important;
}

.second-border {
  border-bottom: 0.2rem double red !important;
}

.sidebar div {
  text-align: center;
}

.sidebar .v-data-table-header__content {
  display: grid; /* Hack to get to make header center align. 'text-align' don't work*/
}

.close_button {
  padding: 0;
}

</style>
