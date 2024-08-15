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
            <span class="text-h5 ">{{ props.pvm }}</span>
					</div>
				</v-col>
			</v-row>
		</template>
    <template #subtitle>
      <v-icon icon="mdi-lead-pencil" />
      <span>{{ props.writer }}</span>
    </template>
	<div class="ma-5">
		<span v-html="vipu ? props.text : jotain()"></span>
		<a 
			@click="vipu =  !vipu"
      class="more"
		>
      {{vipu ? "Näytä vähemmän" : "Näytä enemmän"}}
    </a>
	</div>
	</v-card>
</template>

<script setup>

const props = defineProps({
	title: String,
	text: String,
	writer: String,
	pvm: String,
});

const jotain = () => {
	return props.text.split(" ").slice(0, 150).join(" ") + "...."
}

const vipu = ref(false);

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