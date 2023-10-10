<template>
  <n-config-provider :theme="theme">
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
      <span style="font-size: 18px; font-weight: bold">打卡小助手</span>
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
          <template #header>
            今天打卡了吗
          </template>
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
              :loading="reloadBtn"
              @click="reloadClick"
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
              <template v-if="signInList.length >= 1">
                <n-icon :component="CheckCircle" :size="60" color="#0e7a0d" />
                <span style="font-weight: bold; font-size: 18px">
                  打卡成功，安心上班~
                </span>
                <span>打卡时间： {{ signInList[0].time }}</span>
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
              <template v-if="signInList.length >= 2">
                <n-icon :component="CheckCircle" :size="60" color="#0e7a0d" />
                <span style="font-weight: bold; font-size: 18px">
                  打卡成功，冲啊！下班啦~
                </span>
                <span>打卡时间： {{ signInList[signInList.length-1].time }}</span>
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
    <!-- 弹窗 -->
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
  </n-config-provider>
</template>

<script setup>
import axios from "axios";
import { onMounted, ref, computed, onUnmounted } from "vue";
import { DarkModeFilled, DarkModeOutlined } from "@vicons/material";
import { CheckCircle } from "@vicons/fa";
import { Reload } from "@vicons/ionicons5";
import { QuestionMarkOutlined } from "@vicons/material";
import { SwitchHorizontal } from "@vicons/tabler";
import { createDiscreteApi, darkTheme, lightTheme } from "naive-ui";
import DetailTable from "./DetailTable.vue";
import httpUrl from "./httpUrl";

onMounted(() => {
  if (hasUserID()) return
  const { uId, time } = userInformation.value;
  fetchSignInData({ uId, date: time });
  window.addEventListener("resize", setWindowWidth);
});
onUnmounted(() => {
  window.removeEventListener("resize", setWindowWidth);
});

const windowWidth = ref(document.body.clientWidth);
const signInList = ref([]);
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

const { message } = createDiscreteApi(
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
}

const formatJsonDate = (date) => {
  const formatDate = new Intl.DateTimeFormat("zh", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date(date));
  return formatDate;
};

const fetchSignInData = async (params) => {
  try {
    const data = await axios.get(`${httpUrl}/signIn`, { params });
    signInList.value = data.data.data
      .map((item) => {
        const formatTime = formatJsonDate(item.time);
        const formatReadCardTime = formatJsonDate(item.time);
        return {
          ...item,
          time: formatTime,
          readCardTime: formatReadCardTime,
        };
      })
      .reverse();
  } catch (error) {
    console.log(error);
  }
};

const setTimer = (timer) => {
  return setTimeout(() => {
      message.error("远程响应超时");
      reloadBtn.value = false
      socket.close()
    },1000*60)
}

const wsConnection = () => {
  reloadBtn.value = true
  let timer = null
  const { uId, time } = userInformation.value;
  const socket = new WebSocket("wss://foxconn.devkai.site/api");
  socket.onopen = () => {
    socket.send("queryStart" + uId)
    timer = setTimer()
  }
  socket.onmessage = async ({data}) => {
    clearTimeout(timer)
    timer = setTimer()
    message.info(String(data));
    if (String(data).includes("Task end")) {
      clearTimeout(timer)
      await fetchSignInData({ uId, date: time });
      message.success("刷新成功~");
      reloadBtn.value = false
      socket.close()
    }
  }
  socket.onerror = (error) => {
    console.error(error)
    socket.close()
  }
}

const reloadBtn = ref(false)
const reloadClick = async () => {
  try {
    if (hasUserID()) return
    wsConnection()
  } catch (error) {
    console.log(error);
  }
};

const idSwitch = () => {
  showModal.value = true;
};

const handleCheck = () => {
  localStorage.setItem("uId", uIdInput.value);
  userID.value = uIdInput.value;
  showModal.value = false;
  const { uId, time } = userInformation.value;
  fetchSignInData({ uId, date: time });
};

const tipDrawer = ref(false);
const handleDrawer = () => {
  tipDrawer.value = true
}
</script>

<style scoped>
.idSwitch {
  cursor: pointer;
}
.idSwitch:hover {
  color: #0e7a0d;
}
</style>
