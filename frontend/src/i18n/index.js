import { createI18n } from 'vue-i18n'
import en from './en.js'
import cs from './cs.js'

const savedLanguage = localStorage.getItem('language') || 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLanguage,
  fallbackLocale: 'en',
  messages: { en, cs },
})

export default i18n
