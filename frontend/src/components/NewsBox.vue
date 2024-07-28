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
	<div class="ma-5">
		<span 
			v-html="props.text"
		></span>
	</div>
	</v-card>
</template>

<script setup>

const props = defineProps({
	title: String,
	text: String,
	pvm: String,
})

</script>