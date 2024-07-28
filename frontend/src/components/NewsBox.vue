<template>
	<v-card 
		:title="props.title + ' -  ' + props.pvm"
	>
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