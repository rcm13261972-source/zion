// background.js - Service Worker

chrome.runtime.onInstalled.addListener(() => {
  console.log("Zion Engine Browser Bridge installed.");
});

// This is where we will handle communication between the popup, content script, and CLI Gem.
