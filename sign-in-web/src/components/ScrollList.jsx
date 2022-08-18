import {
  computed,
  defineComponent,
  onMounted,
  ref,
  toRefs,
  toRaw,
  watch,
} from "vue";

const ScrollList = defineComponent({
  props: {
    signInList: {
      type: Array,
      required: true,
    },
    windowWidth: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const { signInList, windowWidth } = toRefs(props);
    const containerHeight = 500;
    const top = ref(0);
    const scrollTop = ref(0);
    const contentHeight = ref(0);
    // 虚拟滚动列表
    const virtualScroll = computed(() => {
      /**
       * moreList模拟数据
       */
      //   const toRawList = toRaw(signInList.value);
      //   let moreList = toRawList;
      //   for (let index = 0; index < 50; index++) {
      //     moreList = [...moreList, ...toRawList];
      //   }
      //   原始数组总长度
      const col = signInList.value.length;
      //   const col = moreList.length;
      //   每个item高度
      const colHeight = 47.39;
      //   定义scroll总高度
      contentHeight.value = colHeight * col + colHeight;
      //   预加载2位防止空白
      const paddingCol = 2;
      //   截取数组开始和结束的下标（可视范围内）
      let startIndex = Math.floor(scrollTop.value / colHeight);
      let endIndex = Math.floor(
        (scrollTop.value + containerHeight) / colHeight
      );
      //   防止数组越界
      startIndex = Math.max(startIndex - paddingCol, 0);
      endIndex = Math.min(endIndex + paddingCol, col - 1);
      //   设置虚拟列表顶部空白节点高度，使列表始终在可视范围
      top.value = colHeight * startIndex;
      //   设置虚拟列表数组
      const items = [];
      for (let i = startIndex; i <= endIndex; i++) {
        // const item = moreList[i];
        const item = signInList.value[i];
        items.push(
          <tr>
            <td>{item.uId}</td>
            <td>{item.name}</td>
            <td>{item.time}</td>
            {windowWidth.value > 992 ? (
              <>
                <td>{item.machine}</td>
                <td>{item.isEffective}</td>
              </>
            ) : null}
          </tr>
        );
      }
      return items;
    });
    return () => (
      <div
        style={{
          marginTop: 20 + "px",
          maxHeight: containerHeight + "px",
          overflow: "auto",
          overflowAnchor: "none",
        }}
        onScroll={(e) => {
          // react用flushSync处理同步任务，异常空白问题，这里未处理
          scrollTop.value = e.target.scrollTop;
        }}
      >
        <div style={{ height: contentHeight.value + "px" }}>
          <n-table bordered={false} single-line={false}>
            <thead>
              <tr>
                <th>工号</th>
                <th>姓名</th>
                <th>打卡时间</th>
                {windowWidth.value > 992 ? (
                  <>
                    <th>打卡卡机</th>
                    <th>是否有效</th>
                  </>
                ) : null}
              </tr>
            </thead>
            <tbody>
              <tr style={{ height: top.value + "px" }}></tr>
              {virtualScroll.value}
            </tbody>
          </n-table>
        </div>
      </div>
    );
  },
});
export default ScrollList;
