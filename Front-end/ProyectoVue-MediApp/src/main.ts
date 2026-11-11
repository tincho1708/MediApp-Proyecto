import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import Avatar from './components/Avatar.vue'

createApp(App).use(createPinia()).component('Avatar', Avatar).mount('#app')
