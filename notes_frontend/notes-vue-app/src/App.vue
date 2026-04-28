<template>
  <div id="app">
    <Navigation />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navigation from './components/Navigation.vue'

// При загрузке приложения проверяем тему
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  const root = document.documentElement

  if (savedTheme === 'dark') {
    root.classList.add('dark-theme')
    root.classList.remove('light-theme')
  } else if (savedTheme === 'light') {
    root.classList.add('light-theme')
    root.classList.remove('dark-theme')
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    root.classList.add('dark-theme')
    root.classList.remove('light-theme')
  } else {
    root.classList.add('light-theme')
    root.classList.remove('dark-theme')
  }
})
</script>

<style>
/* Глобальные CSS переменные для тем */
:root,
:root.light-theme {
  --primary-color: #c9a9e8;
  --primary-hover: #b794d4;
  --primary-light: #f0e6ff;

  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #fafafa;

  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --text-tertiary: #999999;

  --border-color: #e0e0e0;
  --border-light: #f0f0f0;

  --hover-bg: #f5f5f5;
  --active-bg: #f0e6ff;

  --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  --card-shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.1);

  --danger-color: #dc3545;
  --danger-bg: #fee;
  --success-color: #28a745;
  --success-bg: #e8f5e9;

  --modal-overlay: rgba(0, 0, 0, 0.5);
}

:root.dark-theme {
  --primary-color: #b794d4;
  --primary-hover: #c9a9e8;
  --primary-light: #3d2a4d;

  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-tertiary: #242424;

  --text-primary: #e0e0e0;
  --text-secondary: #a0a0a0;
  --text-tertiary: #707070;

  --border-color: #404040;
  --border-light: #333333;

  --hover-bg: #333333;
  --active-bg: #3d2a4d;

  --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  --card-shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.4);

  --danger-color: #ff6b6b;
  --danger-bg: #3d2020;
  --success-color: #51cf66;
  --success-bg: #1e3a2a;

  --modal-overlay: rgba(0, 0, 0, 0.7);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition:
    background-color 0.3s,
    color 0.3s;
}

#app {
  min-height: 100vh;
  background: var(--bg-secondary);
}
</style>
