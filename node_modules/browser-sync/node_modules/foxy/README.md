##Foxy [![Build Status](https://travis-ci.org/shakyShane/foxy.svg?branch=master)](https://travis-ci.org/shakyShane/foxy)

Proxy with response moddin'

**In the near future, the api will be something like:**

```
var proxy = require("foxy");
                    // target               // proxy url
proxy.createServer("http://localsite.dev", "http://localhost:5000");
```

Built-in middleware will re-write html on the fly to update any urls & there'll also be the option
for additional rules for the re-writing.

###Todo

- [x] websocket support
- [ ] accept a url for target
- [ ] test the shit out of the link re-writing


