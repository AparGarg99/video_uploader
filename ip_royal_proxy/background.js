var proxies = [
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-p2idMZjw_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-iNsznEUS_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-0SKVTwBR_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-O1esMJli_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-kIRTd0lT_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-vGssnjyp_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-17WU9BFE_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-kbnTWPs0_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    "krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-np_city-birganj_session-IvO8TRq3_lifetime-30m_streaming-1@geo.iproyal.com:12321",
    // Add more proxies here as needed
];

var currentProxyIndex = 0;

var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "geo.iproyal.com",
            port: parseInt(12321)
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    var proxy = proxies[currentProxyIndex];
    currentProxyIndex = (currentProxyIndex + 1) % proxies.length;
    var credentials = proxy.split('@')[0];
    return {
        authCredentials: {
            username: credentials.split(':')[0],
            password: credentials.split(':')[1]
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {urls: ["<all_urls>"]},
    ['blocking']
);
