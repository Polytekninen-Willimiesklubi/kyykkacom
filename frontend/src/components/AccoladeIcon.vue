<template>
    <v-icon :size="size">
        <img 
            :src="failed ? `src/assets/kyykkalogo120px.png` : `src/assets/accolades/${filename}`"
        />
        <slot></slot>
    </v-icon>
</template>


<script setup>

const props = defineProps({
    filename: String,
    size: {
        type: String,
        default: "24"
    },
});
const failed = ref(false);

if (props.filename === null || props.filename === undefined) {
    failed.value = true;
    console.warn("AccoladeIcon component used without filename prop (" + props.filename + ")")
}

</script>