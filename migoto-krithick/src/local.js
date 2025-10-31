// Function to calculate storage size
function getLocalStorageSizeInMB() {
    let total = 0;
    for (let i = 0; i < localStorage.length; i++) {
      let key = localStorage.key(i);
      let value = localStorage.getItem(key);
  
      // if value is null, count only the key (treat value length as 0)
      let valueLength = value ? value.length : 0;
  
      total += key.length + valueLength;
    }
    let totalBytes = total * 2; // UTF-16 = 2 bytes per char
    let totalMB = totalBytes / (1024 * 1024);
    return totalMB.toFixed(2);
  }


  // Function to update size into localStorage
  function updateLocalStorageSize() {
    const size = getLocalStorageSizeInMB();
    // localStorage.setItem("__localStorageSizeMB", size);
    console.log("Updated localStorage size:", size, "MB");
  }
  
  // Monkey patch setItem & removeItem
  (function () {
    const originalSetItem = localStorage.setItem;
    const originalRemoveItem = localStorage.removeItem;
    const originalClear = localStorage.clear;
  
    localStorage.setItem = function (key, value) {
      originalSetItem.apply(this, arguments);
      updateLocalStorageSize();
    };
  
    localStorage.removeItem = function (key) {
      originalRemoveItem.apply(this, arguments);
      updateLocalStorageSize();
    };
  
    localStorage.clear = function () {
      originalClear.apply(this, arguments);
      updateLocalStorageSize();
    };
  
    // Run once on page load
    updateLocalStorageSize();
  })();