/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'
import LuxonAdapter from "@date-io/luxon"

const luxon = new LuxonAdapter({locale:'fi'});
// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  date: {
    adapter: luxon
  },
  theme: {
    defaultTheme: 'light',
  },
})
