# Checkin Program of SMD Chemnitz in compliance with the Covid Regulations of the Free State of Saxony

This program is used by SMD Chemnitz for checking the vaccination qr codes and saving the contact information, if the person does not use the Corona Warn App. This behavior is required by the current Covid 19 regulations issued by the Free State of Saxony (Freistaat Sachsen).

## Requirements

* python
* pip
* _QT5, OpenCV (will be installed automatically)_

## How to use this program

* run setup.sh in this directory
* start main.py
* the contact information will be saved to the file `<year>-<month>-<day>,json` in the same directory.

## Copyright

2022, Jan Martin Reckel

The vacdec module (files inside the `vacdec`-folder) comes from [this repository](https://github.com/HQJaTu/vacdec) and has been published as public domain (unlicenced).

This program may be used by beneficial organizations for their events (cultural events, church services, etc.). Any other use then that needs the permission of the author.

**Important**: Please be aware that you should handle the data of the registered persons carefully and in accordance with data protection laws! Just delete the JSON-files when the deadline has been riched.