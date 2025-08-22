declare module 'vue-i18n' {
  import Vue, { PluginFunction } from 'vue'
  export interface LocaleMessages {
    [key: string]: any
  }
  export interface I18nOptions {
    locale?: string
    fallbackLocale?: string
    messages?: LocaleMessages
  }
  export default class VueI18n {
    static install: PluginFunction<any>
    constructor(options?: I18nOptions)
    t: (key: string, ...args: any[]) => string
    locale: string
  }
}
