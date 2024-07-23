<template>
  <n-config-provider :theme="theme" :locale="zhCN" :date-locale="dateZhCN">
    <n-layout-header
      style="
        display: flex;
        height: 64px;
        justify-content: center;
        align-items: center;
      "
      bordered
    >
      <div style="position: absolute; left: 20px">
        <!-- 切换账号 -->
        <span style="font-size: 16px; font-weight: bold; margin-right: 12px">
          {{ userID }}
        </span>
        <n-icon
          :component="SwitchHorizontal"
          class="idSwitch"
          @click="idSwitch"
        />
      </div>
      <span style="font-size: 18px; font-weight: bold">打工人的日常</span>
      <div style="position: absolute; right: 20px">
        <n-switch v-model:value="themeSwitch">
          <template #checked-icon>
            <n-icon :component="DarkModeOutlined" />
          </template>
          <template #unchecked-icon>
            <n-icon :component="DarkModeFilled" />
          </template>
        </n-switch>
      </div>
    </n-layout-header>
    <n-layout has-sider style="height: calc(100vh - 128px)">
      <n-layout-sider
        v-if="!isPhone"
        collapse-mode="transform"
        :collapsed-width="20"
        :width="992"
        show-trigger="arrow-circle"
        content-style="padding: 24px;"
        :native-scrollbar="false"
        :default-collapsed="true"
        bordered
      >
        <n-h2>历史打卡信息</n-h2>
        <!-- 数据板块 -->
        <DetailTable />
      </n-layout-sider>
      <n-layout-content
        content-style="padding: 24px;"
        :native-scrollbar="false"
      >
        <!-- 展示板块 -->
        <n-card
          title="今天打卡了吗"
          style="height: calc(100vh - 168px); min-height: 400px"
        >
          <template #header> 今天打卡了吗 </template>
          <template #header-extra>
            <div style="margin-right: 12px">
              <n-button
                strong
                secondary
                circle
                type="info"
                @click="handleDrawer"
              >
                <template #icon>
                  <n-icon :component="QuestionMarkOutlined" />
                </template>
              </n-button>
            </div>
            <n-button
              strong
              secondary
              circle
              type="primary"
              @click="handleReloadModal"
            >
              <template #icon>
                <n-icon :component="Reload" />
              </template>
            </n-button>
          </template>
          <div
            style="
              display: flex;
              height: 100%;
              flex-direction: column;
              align-items: center;
            "
          >
            <div
              style="
                width: 100%;
                height: 100%;
                display: inherit;
                gap: 12px;
                flex-direction: column;
                justify-content: center;
                align-items: center;
              "
            >
              <template v-if="workDay.work">
                <n-icon :component="CheckCircle" :size="60" color="#0e7a0d" />
                <span style="font-weight: bold; font-size: 18px">
                  打卡成功，安心上班~
                </span>
                <span>打卡时间： {{ workDay.work.time }}</span>
              </template>
              <template v-else>
                <n-icon :component="CheckCircle" :size="60" />
                <span style="font-weight: bold; font-size: 18px">
                  还没有打卡信息哦
                </span>
              </template>
            </div>
            <div
              style="
                width: 100%;
                height: 100%;
                display: inherit;
                gap: 12px;
                flex-direction: column;
                justify-content: center;
                align-items: center;
              "
            >
              <template v-if="workDay.offWork">
                <n-icon :component="CheckCircle" :size="60" color="#0e7a0d" />
                <span style="font-weight: bold; font-size: 18px">
                  打卡成功，冲啊！下班啦~
                </span>
                <span>打卡时间： {{ workDay.offWork.time }}</span>
              </template>
              <template v-else>
                <n-icon :component="CheckCircle" :size="60" />
                <span style="font-weight: bold; font-size: 18px">
                  还没有打卡信息哦
                </span>
              </template>
            </div>
          </div>
        </n-card>
        <!-- 数据板块 -->
        <DetailTable v-if="isPhone" />
        <n-back-top :right="25" :bottom="10" />
      </n-layout-content>
    </n-layout>
    <n-layout-footer
      position="absolute"
      style="
        display: flex;
        height: 64px;
        justify-content: center;
        align-items: center;
      "
      bordered
    >
      2022 &copy; FengLeKai
    </n-layout-footer>
    <!-- 设置工号弹窗 -->
    <n-modal v-model:show="showModal">
      <n-card
        style="width: 300px"
        title="设置工号"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <n-input
          style="width: 200px"
          v-model:value="uIdInput"
          placeholder="请输入工号"
          :maxlength="10"
        />
        <template #footer>
          <div style="float: right">
            <n-button
              style="margin-right: 10px"
              size="small"
              @click="showModal = false"
              >取消</n-button
            >
            <n-button type="primary" size="small" @click="handleCheck"
              >确认</n-button
            >
          </div>
        </template>
      </n-card>
    </n-modal>
    <!-- tips弹窗 -->
    <n-drawer v-model:show="tipDrawer" placement="top">
      <n-drawer-content title="提示">
        <n-tag type="info"
          >7:00-10:00,17:00-21:00为获取数据时间,请在结束10分钟前打卡</n-tag
        >
        <br />
        <n-tag style="margin-top: 10px" type="info">自动程序10分钟刷新</n-tag>
        <br />
        <n-tag style="margin-top: 10px" type="info">
          打卡信息存在10分钟左右延迟
        </n-tag>
        <br />
        <n-tag style="margin-top: 10px" type="info">
          如若无法主动刷新请联系管理员
        </n-tag>
      </n-drawer-content>
    </n-drawer>
    <!-- 调用python ws弹窗 -->
    <n-modal
      v-model:show="showReloadModal"
      class="custom-card"
      preset="card"
      :style="{ width: '600px' }"
      title="查询信息"
      size="huge"
      :bordered="false"
    >
      <n-log ref="logInst" :log="log" trim />
      <template #footer>
        <div class="reload-btn-wrapper">
          <n-button
            strong
            secondary
            type="primary"
            :loading="reloadBtn"
            @click="reloadClick"
          >
            查询今日
          </n-button>
          <div class="history-reload">
            <n-date-picker
              type="daterange"
              v-model:value="pickerRange"
              :is-date-disabled="disableDate"
            />
            <n-button
              strong
              secondary
              :loading="historyBtn"
              @click="historyClick"
            >
              查询历史
            </n-button>
          </div>
        </div>
      </template>
    </n-modal>
  </n-config-provider>
</template>

<script setup>
import axios from "axios";
import {
  onMounted,
  ref,
  reactive,
  computed,
  onUnmounted,
  watch,
  nextTick,
} from "vue";
import { DarkModeFilled, DarkModeOutlined } from "@vicons/material";
import { CheckCircle } from "@vicons/fa";
import { Reload } from "@vicons/ionicons5";
import { QuestionMarkOutlined } from "@vicons/material";
import { SwitchHorizontal } from "@vicons/tabler";
import {
  createDiscreteApi,
  darkTheme,
  lightTheme,
  zhCN,
  dateZhCN,
} from "naive-ui";
import DetailTable from "./DetailTable.vue";
import httpUrl from "./httpUrl";
import { formatDate } from "../utils/date.js";
import { workDay as getWorkDay } from "../utils/workDay.js";

onMounted(() => {
  if (hasUserID()) return;
  const { uId, time } = userInformation.value;
  fetchSignInData({ uId, date: time });
  window.addEventListener("resize", setWindowWidth);
});
onUnmounted(() => {
  window.removeEventListener("resize", setWindowWidth);
});

const windowWidth = ref(document.body.clientWidth);
const workDay = ref({
  work: null,
  offWork: null,
});
const userID = ref(localStorage.getItem("uId"));
const userInformation = computed(() => {
  const date = new Date();
  const formatDate = `${date.getFullYear()}-${
    date.getMonth() + 1
  }-${date.getDate()}`;
  return { uId: userID.value, time: formatDate };
});
const uIdInput = ref();
const showModal = ref(false);
const isPhone = computed(() => {
  if (windowWidth.value < 992) {
    return true;
  }
  return false;
});

const themeSwitch = ref(true);
const theme = computed(() => {
  return themeSwitch.value ? lightTheme : darkTheme;
});
const configProviderPropsRef = computed(() => ({
  theme: themeSwitch.value ? lightTheme : darkTheme,
}));

const { message, loadingBar } = createDiscreteApi(
  ["message", "dialog", "notification", "loadingBar"],
  {
    configProviderProps: configProviderPropsRef,
  }
);

const setWindowWidth = () => {
  return (windowWidth.value = document.body.clientWidth);
};

const hasUserID = () => {
  if (!userID.value) {
    message.info("请先设置个工号吧");
    showModal.value = true;
    return true;
  }
  return false;
};

const fetchSignInData = async (params) => {
  try {
    if (!params.uId) return message.warning("未设置工号");
    const data = await axios.get(`${httpUrl}/signIn`, { params });
    console.log(getWorkDay(data.data.data));
    workDay.value = { ...getWorkDay(data.data.data) };
  } catch (error) {
    console.error(error);
  }
};

const setTimer = (socket) => {
  return setTimeout(() => {
    message.error("远程响应超时");
    reloadBtn.value = false;
    historyBtn.value = false;
    socket.close();
  }, 1000 * 60);
};

const wsMsgContent = ref([]);
const wsConnection = (dateRange = "") => {
  let timer = null;
  const { uId, time } = userInformation.value;
  const socket = new WebSocket("wss://foxconn.devkai.site/api");
  socket.onopen = () => {
    socket.send(`[web] ${uId}${dateRange}`);
    timer = setTimer(socket);
  };

  const promise = new Promise((resolve, reject) => {
    socket.onmessage = async ({ data }) => {
      clearTimeout(timer);
      timer = setTimer(socket);
      wsMsgContent.value.push(String(data));
      if (String(data).includes("任务结束")) {
        clearTimeout(timer);
        await fetchSignInData({ uId, date: time });
        message.success("刷新成功~");
        socket.close();
        resolve(true);
      }
    };
    socket.onerror = (error) => {
      console.error(error);
      socket.close();
      reject(error);
    };
  });
  return promise;
};

const reloadBtn = ref(false);
const reloadClick = async () => {
  try {
    if (hasUserID()) return;
    reloadBtn.value = true;
    await wsConnection();
  } catch (error) {
    console.error(error);
  }
  reloadBtn.value = false;
};

const idSwitch = () => {
  showModal.value = true;
};

const handleCheck = () => {
  if (!uIdInput.value) return message.warning("请输入工号");
  localStorage.setItem("uId", uIdInput.value);
  userID.value = uIdInput.value;
  showModal.value = false;
  const { uId, time } = userInformation.value;
  fetchSignInData({ uId, date: time });
};

const tipDrawer = ref(false);
const handleDrawer = () => {
  tipDrawer.value = true;
};

const showReloadModal = ref(false);
const handleReloadModal = () => {
  showReloadModal.value = true;
};

const historyBtn = ref(false);
const pickerRange = ref([Date.now(), Date.now()]);
const disableDate = (ts, type, range) => {
  if (type === "start" && range !== null) {
    const before = range[0] - 1000 * 60 * 60 * 24 * 30;
    const after = range[1] + 1000 * 60 * 60 * 24 * 30;
    return ts < before || ts > after;
  }
  if (type === "end" && range !== null) {
    const before = range[0] - 1000 * 60 * 60 * 24 * 30;
    const after = range[1] + 1000 * 60 * 60 * 24 * 30;
    return ts < before || ts > after;
  }
  return false
};
const historyClick = async () => {
  try {
    if (hasUserID()) return;
    historyBtn.value = true;
    await wsConnection(` ${formatDate(pickerRange.value[0])}-${formatDate(pickerRange.value[1])}`);
  } catch (error) {
    console.error(error);
  }
  historyBtn.value = false;
};

const log = computed(() => {
  return wsMsgContent.value.join("\n") + "\n";
});
const logInst = ref(null);
watch(
  () => log.value,
  () => {
    nextTick(() => {
      logInst.value?.scrollTo({ position: "bottom", silent: true });
    });
  }
);
</script>

<style scoped>
.idSwitch {
  cursor: pointer;
}
.idSwitch:hover {
  color: #0e7a0d;
}
.reload-btn-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.history-reload {
  display: flex;
  justify-content: flex-end;
}
.history-reload > * + * {
  margin-left: 12px;
}
</style>
