<template>
  <!-- 数据板块 -->
  <!-- 日历 -->
  <div>
    <div style="overflow: hidden; margin-top: 20px">
      <n-button style="float: right; margin-left: 12px" @click="reloadClick">
        <template #icon>
          <n-icon :component="Reload" />
        </template>
        刷新
      </n-button>
    </div>
    <div style="margin-top: 20px">
      <n-card>
        <Calendar :signInDays="signInDays" />
      </n-card>
    </div>
    <!-- 表格 -->
    <div style="margin-top: 20px">
      <n-card title="这是查询">
        <div style="display: flex; gap: 12px 12px; flex-wrap: wrap">
          <n-input
            style="width: 200px; margin-bottom: 10px"
            v-model:value="uIdInput"
            clearable
            placeholder="请输入工号"
            :maxlength="10"
            @input="uIdInputChange"
          />
          <n-date-picker
            style="width: 200px"
            v-model:value="datePicker"
            value-format="yyyy-MM-dd"
            clearable
            type="date"
            placeholder="请选择日期"
            @update:formatted-value="datePickerChange"
            @clear="pickerClear"
          />
        </div>
      </n-card>
      <ScrollList :signInList="signInList" :windowWidth="windowWidth" />
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { onMounted, ref, computed, onUnmounted } from "vue";
import { createDiscreteApi, darkTheme, lightTheme } from "naive-ui";
import { Reload } from "@vicons/ionicons5";
import httpUrl from "./httpUrl";
import ScrollList from "./ScrollList.jsx";
import Calendar from "./Calendar.vue";
import { formatJsonDate } from "../utils/date.js";
import { isOffWorkTime } from "../utils/workDay.js";

onMounted(() => {
  fetchSignInData();
  window.onresize = () => {
    return (windowWidth.value = document.body.clientWidth);
  };
});
onUnmounted(() => {
  window.onresize = null;
});

const themeSwitch = ref(true);
const configProviderPropsRef = computed(() => ({
  theme: themeSwitch.value ? lightTheme : darkTheme,
}));

const { message, loadingBar } = createDiscreteApi(
  ["message", "dialog", "notification", "loadingBar"],
  {
    configProviderProps: configProviderPropsRef,
  }
);

const signInList = ref([]);
const windowWidth = ref(document.body.clientWidth);
const uIdInput = ref();
const datePicker = ref();
const dateFormatValue = ref();

const signInDays = computed(() => {
  /**
   * 数字代表签到数量
   * 1: 上班已签到
   * 2：上班、下班已签到
   * {
   *  2024-07-11: 1
   *  2024-07-12: 2
   * }
   */
  const res = {};
  signInList.value.forEach((item) => {
    const uId = localStorage.getItem("uId");
    if (uId === item.uId) {
      const key = item.time.split(" ")[0];
      
      if (!res[key]) res[key] = 1;
      if (isOffWorkTime(item.time)) {
        res[key] = 2;
      }
    }
  });
  return res;
});

const fetchSignInData = async (params) => {
  loadingBar.start();
  try {
    const uId = localStorage.getItem("uId");
    if (!uId) {
      message.warning("未设置工号");
      loadingBar.error();
      return;
    }
    const data = await axios.get(`${httpUrl}/signIn`, {
      params: { uId, ...params },
    });
    signInList.value = data.data.data.map((item) => {
      const formatTime = formatJsonDate(item.time);
      const formatReadCardTime = formatJsonDate(item.readCardTime);
      return {
        ...item,
        time: formatTime,
        readCardTime: formatReadCardTime,
      };
    });
  } catch (error) {
    console.log(error);
    loadingBar.error();
    throw error
  }
  loadingBar.finish();
};

const reloadClick = async () => {
  try {
    await fetchSignInData();
    message.success("刷新成功~");
  } catch (error) {
    message.error("刷新失败");
    console.log(error);
  }
};

function debounce(fn, delay) {
  let timer; // 维护一个 timer
  return function () {
    let _this = this; // 取debounce执行作用域的this
    let args = arguments;
    if (timer) {
      console.log(timer);
      clearTimeout(timer);
    }
    timer = setTimeout(function () {
      fn.apply(_this, args); // 用apply指向调用debounce的对象，相当于_this.fn(args);
    }, delay);
  };
}

const uIdInputChange = debounce((value) => {
  if (!value) return fetchSignInData();
  fetchSignInData({ uId: value, date: dateFormatValue.value });
}, 1000);

const datePickerChange = async (value) => {
  if (!value) return fetchSignInData();
  dateFormatValue.value = value;
  fetchSignInData({ uId: uIdInput.value, date: value });
};

const pickerClear = () => {
  dateFormatValue.value = null;
  fetchSignInData();
};
</script>

<style scoped></style>
