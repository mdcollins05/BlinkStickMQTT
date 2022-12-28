# BlinkStickMQTT

This is a simple service that will listen to an MQTT topic and react to color and TTL sent to the topic. I'm using it as a visual alert for various things from Home Assistant via Node Red.

The service expects messages in the following format:

`#(hex_color),(ttl_in_seconds)`

For example:

`#660000,60`

Would light up any BlinkStick(s) listening red for 60 seconds.

It also supports alternating between multiple colors and each color would display for their respective TTL.
