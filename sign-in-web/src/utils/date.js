export const formatJsonDate = (date) => {
    // 匹配 ISO 8601 格式的时间戳
    const regex = /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}).\d{3}Z$/;
    const match = date.match(regex);

    if (match) {
        const datePart = match[1];
        const timePart = match[2];
        return `${datePart} ${timePart}`;
    } else {
        // 如果时间戳格式不匹配，返回原始值
        return date;
    }
};

const zeroPadding = (number) => {
    return number < 10 ? "0" + number : number
}

export const formatDate = (dateTime) => {
    const curDate = new Date(dateTime)
    const year = curDate.getFullYear()
    const month = zeroPadding(curDate.getMonth() + 1)
    const date = zeroPadding(curDate.getDate())
    
    return `${year}/${month}/${date}`
}

export default formatJsonDate