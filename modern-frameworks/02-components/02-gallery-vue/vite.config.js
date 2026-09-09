import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    // Псевдонім @ вказує на src: шлях до токенів не залежить від того,
    // на якій глибині лежить компонент.
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },

  css: {
    preprocessorOptions: {
      scss: {
        // Токени й міксини підставляються на початок кожного блоку
        // <style lang="scss">. Сюди можна класти лише те, що саме по собі
        // не породжує CSS: змінні, міксини, функції. Звичайне правило,
        // покладене сюди, продублювалося б у стилях кожного компонента.
        additionalData: '@use "@/styles/tokens" as *;\n@use "@/styles/mixins" as *;\n',
      },
    },
  },
})
