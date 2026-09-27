/* Vercel Web Analytics - Initialization Script */
(function() {
  // Initialize the analytics queue
  window.va = window.va || function() {
    (window.vaq = window.vaq || []).push(arguments);
  };
  
  // Determine the script source URL
  // This will use Vercel's hosted analytics script when deployed
  var scriptSrc = '/_vercel/insights/script.js';
  
  // Check if script is already loaded
  if (document.head.querySelector('script[src*="' + scriptSrc + '"]')) {
    return;
  }
  
  // Create and append the analytics script
  var script = document.createElement('script');
  script.src = scriptSrc;
  script.defer = true;
  script.dataset.sdkn = '@vercel/analytics';
  script.dataset.sdkv = '1.6.1';
  
  script.onerror = function() {
    console.log(
      '[Vercel Web Analytics] Failed to load analytics script. ' +
      'Please enable Web Analytics in your Vercel project settings.'
    );
  };
  
  document.head.appendChild(script);
})();
