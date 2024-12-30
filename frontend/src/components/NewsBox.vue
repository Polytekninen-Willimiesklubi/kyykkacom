<template>
	<v-card>
		<template #title>
			<v-row>
				<v-col>
					<span class="text-h5">{{ props.title }}</span>
				</v-col>
				<v-spacer />
				<v-col class="">
          <div class="d-flex justify-end">
						<span class="text-h5 ">
							{{ date.formatByString(date.date(props.date), 'dd.MM.yyyy') }}
						</span>
					</div>
				</v-col>
			</v-row>
		</template>
    <template #subtitle>
      <v-icon icon="mdi-lead-pencil" />
      <span>{{ props.writer }}</span>
    </template>
	<div class="ma-5">
		<span v-html="showAll | !smallText() ? props.text : smallText()"></span>
		<a v-if="smallText()"
			@click="showAll = !showAll"
      		class="more"
		>
      {{showAll ? "Näytä vähemmän" : "Näytä enemmän"}}
    </a>
	</div>
	</v-card>
</template>

<script setup>

import { useDate } from 'vuetify';

const props = defineProps({
	title: String,
	text: String,
	writer: String,
	date: String,
});

const date = useDate();

const smallText = () => {
	if (props.text.length < 150) {
		return null
	}
	return props.text.split(" ").slice(0, 150).join(" ") + "...."
}

const showAll = ref(false);

</script>

<style scoped>
.more {
  color : blue;
  font: 0.9em sans-serif;
}

.more:hover {
  text-decoration: underline;
  cursor: pointer;
}

</style>