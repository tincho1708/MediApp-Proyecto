import Avatar from './components/Avatar.vue'

declare module 'vue' {
  interface GlobalComponents {
    Avatar: typeof Avatar
  }
}

export {}
