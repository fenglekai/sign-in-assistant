
import { formatJsonDate } from './date.js'

const offTime = '17:30:00'

function setOffTime(date) {
  const dateTime = new Date(date)
  return new Date(`${dateTime.getFullYear()}-${dateTime.getMonth()+1}-${dateTime.getDate()} ${offTime}`)
}

export function isOffWorkTime(date) {
  return new Date(date) > setOffTime(date)
}

export function workDay(data = []) {
    const workSignIn = {
        work: null,
        offWork: null
    }
    // 数据最大时间优先输出
    for (const iterator of data) {
        if (workSignIn.offWork) continue;
        if (workSignIn.work) break;
        const temp = {
          ...iterator,
          time: formatJsonDate(iterator.time),
          readCardTime: formatJsonDate(iterator.readCardTime),
        };
        const signInTime = new Date(temp.time)
        const offWorkTime = setOffTime(temp.time)
        if (signInTime < offWorkTime) {
          workSignIn.work = temp
        } else {
          workSignIn.offWork = temp
        }
      }
    return workSignIn
}

export default workDay