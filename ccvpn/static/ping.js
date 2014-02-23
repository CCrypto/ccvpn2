function ping(host, callback) {
    var start;
    var done = false;
    var img = new Image();
    function ok() {
        done = true;
        var time = new Date() - start;
        callback(time + 'ms');
    }
    function fail() {
        if (!done) {
            callback('timeout');
        }
    }
    img.onload = ok;
    img.onerror = ok;
    start = new Date();
    img.src = host;
    var timer = setTimeout(fail, 1500);
    return '[ping: ...]';
}

window.addEventListener('load', function() {
    var lines = document.getElementsByClassName('host_line');
    for (var i=0; i<lines.length; i++) {
        var line = lines[i];
        
        var ping_link = document.createElement('a');
        ping_link.href = '#';
        ping_link.innerHTML = '[ping]';
        ping_link.onclick = (function(line) {
            return function() {
                result = ping('http://' + line.children[0].innerHTML + '/ping',
                    function(r) {
                        line.children[1].innerHTML = '[ping: '+r+']';
                    });
                return false;
            }
        })(line);
        line.appendChild(ping_link);
    }
}, false);

