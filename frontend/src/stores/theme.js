import { defineStore } from 'pinia';
import { ref, watchEffect } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  // --- STATE ---
  // Initialize theme from the user's saved preference in localStorage,
  // or default to light mode (isDark = false).
  const isDark = ref(localStorage.getItem('isDarkTheme') === 'true');

  // --- ACTION ---
  /**
   * Toggles the theme between light and dark and saves the preference.
   */
  const toggleTheme = () => {
    isDark.value = !isDark.value;
    localStorage.setItem('isDarkTheme', isDark.value);
  };

  // --- EFFECT ---
  /**
   * This is the key part. It automatically adds or removes a 'dark-theme'
   * class to your application's main body tag whenever the theme changes.
   * This allows us to control the theme with pure CSS.
   */
  watchEffect(() => {
    const body = document.body;
    if (isDark.value) {
      body.classList.add('dark-theme');
    } else {
      body.classList.remove('dark-theme');
    }
  });

  return {
    isDark,
    toggleTheme,
  };
});