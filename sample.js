function processData(data) {
    let result = [];
    for (let i = 0; i < data.length; i++) {
        let currentItem = data[i];
        if ('id' in currentItem) {
            result.push({ id: currentItem['id'], value: 42 });
        } else {
            result.push(currentItem);
        }
    }
    return result;
}