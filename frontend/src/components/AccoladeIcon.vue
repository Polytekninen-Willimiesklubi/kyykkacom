<template>
    <v-icon :size="size">
        <img 
            :src="imageIndex[props.filename]"
            alt="src/assets/kyykkalogo120px.png"
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

// FIXME Do better
const imageIndex = {
    "hauki.png": require("@/assets/accolades/hauki.png"),
    "hopea.ico": require("@/assets/accolades/hopea.ico"),
    "joulukuusen_kaataja.png": require("@/assets/accolades/joulukuusen_kaataja.png"),
    "lakaisija.png": require("@/assets/accolades/lakaisija.png"),
    "mestari.ico": require("@/assets/accolades/mestari.ico"),
    "mvp.png": require("@/assets/accolades/mvp.png"),
    "naismies_paras.svg": require("@/assets/accolades/naismies_paras.svg"),
    "pronssi.ico": require("@/assets/accolades/pronssi.ico"),
    "pudotus.ico": require("@/assets/accolades/pudotus.ico"),
    "runkomestari.ico": require("@/assets/accolades/runkomestari.ico"),
    "runkosarja_paras.ico": require("@/assets/accolades/runkosarja_paras.ico"),
    "superweekend.ico": require("@/assets/accolades/superweekend.ico"),
    "tulokas.ico": require("@/assets/accolades/tulokas.ico"),
    "vuoden_kyykkaaja.svg": require("@/assets/accolades/vuoden_kyykkaaja.svg"),
    "vuoden_tulokas.svg": require("@/assets/accolades/vuoden_tulokas.svg"),
}

if (props.filename === null || props.filename === undefined) {
    failed.value = true;
    console.warn("AccoladeIcon component used without filename prop (" + props.filename + ")")
}

</script>