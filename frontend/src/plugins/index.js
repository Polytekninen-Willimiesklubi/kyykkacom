/**
 * plugins/index.js
 *
 * Automatically included in `./src/main.js`
 */

// Plugins
import vuetify from './vuetify'
import pinia from '@/stores'
import router from '@/router'
import PrimeVue from 'primevue/config'
import Editor from 'primevue/editor'

export function registerPlugins (app) {
  app
    .use(vuetify)
    .use(router)
    .use(pinia)
    .use(PrimeVue, { unstyled: true })
    .component('Editor', Editor)
}
