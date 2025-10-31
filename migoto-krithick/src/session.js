// Function to calculate sessionStorage size
function getSessionStorageSizeInMB() {
    let total = 0;
    for (let key in sessionStorage) {
      if (sessionStorage.hasOwnProperty(key)) {
        let value = sessionStorage.getItem(key);
        total += key.length + value.length;
      }
    }
    let totalBytes = total * 2; // UTF-16 = 2 bytes per char
    let totalMB = totalBytes / (1024 * 1024);
    return totalMB.toFixed(2);
  }
  
  // Function to update size into sessionStorage
  function updateSessionStorageSize() {
    const size = getSessionStorageSizeInMB();
    sessionStorage.setItem("__sessionStorageSizeMB", size);
    console.log("Updated sessionStorage size:", size, "MB");
  }

  // Monkey patch setItem, removeItem, and clear for sessionStorage
  (function () {
    const originalSetItem = sessionStorage.setItem;
    const originalRemoveItem = sessionStorage.removeItem;
    const originalClear = sessionStorage.clear;
  
    sessionStorage.setItem = function (key, value) {
      originalSetItem.apply(this, arguments);
      updateSessionStorageSize();
    };
  
    sessionStorage.removeItem = function (key) {
      originalRemoveItem.apply(this, arguments);
      updateSessionStorageSize();
    };
  
    sessionStorage.clear = function () {
      originalClear.apply(this, arguments);
      updateSessionStorageSize();
    };
  
    // Run once on page load
    updateSessionStorageSize();
  })();
  