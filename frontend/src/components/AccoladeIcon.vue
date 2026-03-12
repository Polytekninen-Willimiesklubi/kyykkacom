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
import hauki from "@/assets/accolades/hauki.png";
import hopea from "@/assets/accolades/hopea.ico";
import joulukuusen_kaataja from "@/assets/accolades/joulukuusen_kaataja.png";
import lakaisija from "@/assets/accolades/lakaisija.png";
import mestari from "@/assets/accolades/mestari.ico";
import mvp from "@/assets/accolades/mvp.png";
import naismies_paras from "@/assets/accolades/naismies_paras.svg";
import pronssi from "@/assets/accolades/pronssi.ico";
import pudotus from "@/assets/accolades/pudotus.ico";
import runkomestari from "@/assets/accolades/runkomestari.ico";
import runkosarja_paras from "@/assets/accolades/runkosarja_paras.ico";
import superweekend from "@/assets/accolades/superweekend.ico";
import tulokas from "@/assets/accolades/tulokas.ico";
import vuoden_kyykkaaja from "@/assets/accolades/vuoden_kyykkaaja.svg";
import vuoden_tulokas from "@/assets/accolades/vuoden_tulokas.svg";

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
    "hauki.png": hauki,
    "hopea.ico": hopea,
    "joulukuusen_kaataja.png": joulukuusen_kaataja,
    "lakaisija.png": lakaisija,
    "mestari.ico": mestari,
    "mvp.png": mvp,
    "naismies_paras.svg": naismies_paras,
    "pronssi.ico": pronssi,
    "pudotus.ico": pudotus,
    "runkomestari.ico": runkomestari,
    "runkosarja_paras.ico": runkosarja_paras,
    "superweekend.ico": superweekend,
    "tulokas.ico": tulokas,
    "vuoden_kyykkaaja.svg": vuoden_kyykkaaja,
    "vuoden_tulokas.svg": vuoden_tulokas,
};

if (props.filename === null || props.filename === undefined) {
    failed.value = true;
    console.warn("AccoladeIcon component used without filename prop (" + props.filename + ")")
}

</script>