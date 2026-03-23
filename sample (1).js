function processData(data) {
    // Initialize an empty array to store the processed data
    let result = [];
    
    // Iterate over each item in the input data
    for (let i = 0; i < data.length; i++) {
        // Get the current item from the data array
        let currentItem = data[i];
        
        // Check if the current item has an 'id' property
        if ('id' in currentItem) {
            // If it does, create a new object with 'id' and 'value' properties and push it to the result array
            result.push({ id: currentItem['id'], value: 42 });
        } else {
            // If it doesn't, simply push the current item to the result array as is
            result.push(currentItem);
        }
    }
    
    // Return the processed data
    return result;
}