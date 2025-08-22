import 'babel-polyfill'
import Vue from 'vue'
import App from './App.vue'
import router from './routes'
import store from './store'
import vuetify from './plugins/vuetify'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)

const messages = {
  zh: {
    common: {
      welcomeBack: '欢迎回来！',
      logout: '退出登录',
      help: '帮助',
      user: '用户',
      collapseSidebar: '收起侧边栏',
      selectProject: '选择项目',
      project: '项目',
      home: '首页',
      workflows: '工作流',
      extensions: '扩展',
    }
  },
  en: {
    common: {
      welcomeBack: 'Welcome back!',
      logout: 'Log Out',
      help: 'Help',
      user: 'User',
      collapseSidebar: 'Collapse Sidebar',
      selectProject: 'Select a project',
      project: 'Project',
      home: 'Home',
      workflows: 'Workflows',
      extensions: 'Extensions',
    }
  }
}

const i18n: any = new VueI18n({
  locale: 'zh',
  fallbackLocale: 'en',
  messages
})

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  vuetify,
  i18n,
  render: (h) => h(App),
}).$mount('#app');
