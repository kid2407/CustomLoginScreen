# Custom Login Screen

This combination of nginx configurations and a python script allows you to apply custom CSS per world on your Foundry instance.

This setup requires the following components:

* A running Foundry instance
* An NGINX server configured as a reverse proxy for Foundry (see [the wiki](https://foundryvtt.com/article/installation/#dedicated) for details on how to set that up)
* Python 3

## Setup

The following steps are needed to set up the tool correctly:

### Adjust NGINX configuration

The snippets for the nginx config supplied with this tool are as follows:

```nginx
# Add this part to the http directive in your nginx.conf
http {
    log_format postdata escape=none $request_body;
}
```
```nginx
# Add this in your nginx configuration file, replace <host> with your relevant data
server {

    # [...]

    location / {
        # Some magic to get around nginx not supporting multiple ifs
        set $test root;
        if ($request_method = POST) {
            set $test "${test}-post";
        }
        if ( $request_uri = /setup) {
            set $test "${test}-setup";
        }

        if ($test = root-post-setup) {
            # Feel free to rename the file name as needed
            access_log /var/log/nginx/foundry_setup_calls.log postdata;
        }

        # Rest of the config where you pass the request to Foundry
    }
}
```

The first section contains the instruction `log_format`, which tells nginx to log the request body when someone uses the log format named "postdata". This has to be placed in your `nginx.conf` inside the `http` directive.

The second part shows the relevant section that has to be added to the nginx configuration file for foundry (the one you use when [setting it up](https://foundryvtt.com/article/installation/#dedicated)). The snippet inside the `location /` directive has to be added before you send the request to Foundry, meaning before the `proxy_pass` call.

Make sure to check for potential config errors with `nginx -t` and reload nginx to apply the changes.

### Prepare the watch script

The script watchFoundryLog.py can be placed anywhere you like, just make sure it has write and read permissions for Foundry's style.css as well as for its own directory. Once placed you can simply run it, preferably in a `screen`, so you don't have to be connected to the server all the time. It takes two arguments, you can see the details for it by calling `python3 watchFoundryLog.py --help`:
```
usage: watchFoundryLog.py [-h] log_file_path foundry_path

positional arguments:
    log_file_path  The path of the log file where nginx logs the requests we are interested in. Use "reset" to put the original style back in place.
    foundry_path   The path to the root of your foundry install.

optional arguments:
    -h, --help     show this help message and exit
```

### Preparing the custom CSS files

For the tool to parse and automatically apply your custom sheets, simply place them in the `styles` folder. it is automatically created when you run the tool for the first time, or you can manually create it.
The file has to be named like the world it should be applied to, so if your world is named `my-awesome-world`, the file should be named `my-awesome-world.css`

## Running the script

If we assume that our Foundry install lives in `/home/me/foundry` and the log file is located at `/var/log/nginx/foundry_setup_calls.log, we can call the script the following way:
```shell
python3 watchFoundryLog.py /var/log/nginx/foundry_setup_calls.log /home/me/foundry
```