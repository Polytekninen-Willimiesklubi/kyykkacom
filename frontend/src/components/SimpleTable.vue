<template>
    <v-card 
        :title="props.title"
        class="ma-5" 
        style="align-self: start;"
    >
        <v-data-table
            :mobile-breakpoint="0"
            class="hof_table"
            :headers="props.headers"
            :items="props.items"
            items-per-page="-1"
            density="compact"
            :disable-sort="!props.sortable"
        >
            <template v-for="header in props.headers"
                #[`header.${header.key}`]="{ column, toggleSort, getSortIcon }"
            >
                <v-tooltip :text="column.tooltip" v-if="column.tooltip" location="top">
                    <template #activator="{ props }">
                    <div class="v-data-table-header__content" v-bind="props">
                        <!-- HACK To properly center column header with the sort icon
                                just add another span to other side -->
                        <span v-if="column.align !== 'left' && props.sortable" style="width:14px"></span>
                        <span @click="() => toggleSort(column)">{{ column.title }}</span>
                        <v-icon v-if="column.sortable && props.sortable"
                            class="v-data-table-header__sort-icon" 
                            :icon="getSortIcon(column)"
                            size="x-small"
                        />
                    </div>
                    </template>
                </v-tooltip>
                <template v-else>
                    <div class="v-data-table-header__content">
                    <!-- HACK To properly center column header with the sort icon
                                just add another span to other side -->
                    <span v-if="column.align !== 'left' && props.sortable" style="width:14px"></span>
                    <span @click="() => toggleSort(column)">{{ column.title }}</span>
                    <v-icon v-if="column.sortable && props.sortable" 
                        class="v-data-table-header__sort-icon" 
                        :icon="getSortIcon(column)"
                        size="x-small"
                    />
                    </div>
                </template>
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
    sortable: {
        type: Boolean,
        default: false
    }
})




</script>
<style scoped>
.hof_table tr {
  text-align: center;
}
</style>