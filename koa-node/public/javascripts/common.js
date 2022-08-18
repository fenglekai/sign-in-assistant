function responseBodyFormat(data = null, msg = 'success', status = 200) {
    return {
        data,
        msg,
        status
    }
}

module.exports = {
    responseBodyFormat
}