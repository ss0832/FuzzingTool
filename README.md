# FuzzingTool
Fuzzing tool for web application penetration test

## Warning

Use this program only in your own environment and do not use it in someone else's environment without permission.


## Example

```
python .\netfuzz.py [host name] -f fuzz1 list_1.txt fuzz2 list_2.txt -p http tcp 80 -t 1.0 -mt 1 -d templete_data.header
```

## Options

`-f [input xxx1 to replace @@@xxx1@@@ to content of yyy1.txt] yyy1.txt [input xxx2 to replace @@@xxx2@@@ to content of yyy2.txt] yyy2.txt -d templete_data.header`

This program change @@@xxx1@@@ in templete_data.header into the content of yyy1.txt.

This program change @@@xxx2@@@ in templete_data.header into the content of yyy2.txt.

And, this python program send the content of templete_data.header to the server you specify hostname.

`-p [transmission protocol (available) http, https] [tcp or udp] [port number]`

Default settings are "https", "tcp", and 443.

`mt [number of threads]`

This argument is for multithread processing. Default setting is 150.




## License

License of this program is MIT License.
