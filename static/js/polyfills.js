
// Browser Compatibility Polyfills

// Array.from polyfill for IE
if (!Array.from) {
    Array.from = function(arrayLike) {
        return Array.prototype.slice.call(arrayLike);
    };
}

// Element.matches polyfill for IE
if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector || 
                               Element.prototype.webkitMatchesSelector;
}

// Element.closest polyfill for IE
if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
        var el = this;
        do {
            if (el.matches(s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}

// CustomEvent polyfill for IE
if (typeof window.CustomEvent !== 'function') {
    function CustomEvent(event, params) {
        params = params || { bubbles: false, cancelable: false, detail: null };
        var evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
    }
    CustomEvent.prototype = window.Event.prototype;
    window.CustomEvent = CustomEvent;
}

// fetch polyfill for older browsers
if (!window.fetch) {
    window.fetch = function(url, options) {
        return new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open(options.method || 'GET', url);
            
            if (options.headers) {
                Object.keys(options.headers).forEach(function(key) {
                    xhr.setRequestHeader(key, options.headers[key]);
                });
            }
            
            xhr.onload = function() {
                resolve({
                    ok: xhr.status >= 200 && xhr.status < 300,
                    status: xhr.status,
                    statusText: xhr.statusText,
                    text: function() { return Promise.resolve(xhr.responseText); },
                    json: function() { return Promise.resolve(JSON.parse(xhr.responseText)); }
                });
            };
            
            xhr.onerror = function() {
                reject(new Error('Network error'));
            };
            
            xhr.send(options.body);
        });
    };
}
