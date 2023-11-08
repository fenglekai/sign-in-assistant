import { createApp } from "vue";
import App from "./App.vue";
import {
  create,
  NButton,
  NSpace,
  NLayout,
  NLayoutHeader,
  NLayoutSider,
  NLayoutContent,
  NLayoutFooter,
  NH2,
  NTable,
  NAlert,
  NSwitch,
  NIcon,
  NConfigProvider,
  NDrawer,
  NDrawerContent,
  NCard,
  NInput,
  NTag,
  NDatePicker,
  NH3,
  NModal,
  NBackTop,
  NScrollbar,
  NEmpty,
} from "naive-ui";
// 通用字体
import "vfonts/Lato.css";
// 等宽字体
import "vfonts/FiraCode.css";

const naive = create({
  components: [
    NButton,
    NSpace,
    NLayout,
    NLayoutHeader,
    NLayoutSider,
    NLayoutContent,
    NLayoutFooter,
    NH2,
    NH3,
    NTable,
    NAlert,
    NSwitch,
    NIcon,
    NConfigProvider,
    NDrawer,
    NDrawerContent,
    NCard,
    NInput,
    NTag,
    NDatePicker,
    NModal,
    NBackTop,
    NScrollbar,
    NEmpty,
  ],
});

const app = createApp(App);
app.use(naive);
app.mount("#app");
