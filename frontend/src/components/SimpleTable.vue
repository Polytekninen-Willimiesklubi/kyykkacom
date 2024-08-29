<template>
    <v-card 
        :title="props.title"
        class="ma-5" 
        style="align-self: start;"
    >

        <v-data-table
            mobile-breakpoint="0"
            class="hof_table"
            :headers="props.headers"
            :items="props.items"
            items-per-page="-1"
            density="compact"
        >
            <template #headers="{ columns }">
                <tr>
                    <template v-for="column in columns" :key="column.key">
                        <td>
                            {{ column.title }}
                            <v-tooltip
                                v-if="column.tooltip"
                                activator="parent"
                                location="top"
                                :text="column.tooltip"
                            />
                        </td>
                    </template>
                </tr>
            </template>
            <template #bottom><slot name="bottom_legend"></slot></template>
        </v-data-table>
    </v-card>
</template>

<script setup>

const props = defineProps({
  title: String,
  headers: Array,
  items: Array,
})


</script>
<style scoped>
.hof_table tr {
  text-align: center;
}
</style>