<template>
    <v-card class="mr-5">
        <v-row>
            <v-spacer/>
            <v-col align="center">
                Säännöt vuodelta:
            </v-col>
            <v-col cols="6" align="center">
                <v-select 
                    v-model="saannot"
                    :items="[
                        '2023',
                        '2024',
                        '2025',
                    ]"
                    item-color="red"
                />
            </v-col>
            <v-spacer/>
        </v-row>
        <v-row>
            <v-col>
                <object height="900" width="1000" :data="'/saannot_'+saannot+'.pdf'"></object>
            </v-col>
        </v-row>
    </v-card>
</template>

<route lang="yaml">
    meta:
        layout: "withoutSidebar"
</route>

<script setup>

const saannot = ref("2025");

</script>
<style>
.rules__link {
  text-decoration: none;
  color: red !important;
}

</style>