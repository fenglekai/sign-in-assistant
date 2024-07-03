const addZero = (number) => {
  return number < 10 ? `0${number}` : number
}

export const formatJsonDate = (date) => {
  // const formatDate = new Intl.DateTimeFormat("zh", {
  //   year: "numeric",
  //   month: "2-digit",
  //   day: "2-digit",
  //   hour: "2-digit",
  //   minute: "2-digit",
  //   second: "2-digit",
  //   hour12: false,
  // }).format(new Date(date));
  // const res = formatDate.replaceAll('/','-')
  const nowDate = new Date(date);
  const res = `${nowDate.getFullYear()}-${
    addZero(nowDate.getMonth() + 1)
  }-${addZero(nowDate.getDate())} ${addZero(nowDate.getHours())}:${addZero(nowDate.getMinutes())}:${addZero(nowDate.getSeconds())}`;
  return res;
};
