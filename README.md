# FuzzingTool
Fuzzing tool for web application penetration test

## Warning

Use this program only in your own environment and do not use it in someone else's environment without permission.


## Example

```
python .\netfuzz.py [host name] -f fuzz1 list_1.txt fuzz2 list_2.txt -p http tcp 80 -t 1.0 -mt 1 -d templete_data.header
```

This program change @@@fuzz1@@@ in templete_data.header into the content of list_1.txt.

This program change @@@fuzz2@@@ in templete_data.header into the content of list_2.txt.

And, this python program send the content of templete_data.header to the server you specify hostname.

## License

License of this program is MIT License.
