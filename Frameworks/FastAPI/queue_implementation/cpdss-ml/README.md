# CPDSS ML Dockerfile

[Docker](http://docker.com) container to use CPDSS ML.

## Install

build from source (in the folder directory with the dockerfile):
```
    docker build . -t <NAME OF DOCKER IMAGE>
```
## Run

Run the image, binding associated ports, and mounting the present working
directory:
```
    docker run -p 8000:8000 <NAME OF DOCKER IMAGE>
```


## Services

Service      | Port | Usage
-------------|------|------
CPDSS ML     | 8000 | visit localhost:8000/docs to access FastAPI UI


## Volumes

Volume          | Description
----------------|-------------
`/app`          | The location of the CP-DSS ML application root.

## Usage
There are 5 APIs in this Application
### 1) Pump Rates Estimation
Given port, vessel and theoretical max rate at port, the API will output the estimated bulk discharge rate for that port using historical records.
<br>
Input:
 ``` 
 POST /pumprates
{
  "Port": "Kawasaki",
  "Vessel": "Kazusa",
  "MaxRate": 13500
}
```
Output (if historical data is available):
```
{
    "vessel": "Gassan",
    "port": "Kawasaki",
    "Pump Rates (KL/hrs)": 12056.169805609305,
    "Theoretical Max(KL/hrs)": 13500.0
} 
```
Output (if no historical data is available):
```
null
```

### 2) Cargo API, Temperature Estimation
Given port, cargo and the date, the api will output an estimate of the cargo API and temperature at that week of the year.
<br>
For example, 3 Jan 2022 lies on the 1st week of the year. Thus, the API will estimate the cargo API and temperature for the 1st week of the year.
<br>
Input:
``` 
 POST /cargo
{
  "Port": "Mina Al Fahal",
  "Cargo": "Oman Export",
  "Year": 2013,
  "Month": 6,
  "Date": 9
  }
```
Output:
```
{
    "port": "Mina Al Fahal",
    "cargo": "Oman Export",
    "api": 30.972765957446793,
    "temp (F)": 111.92500000000001,
    "date": "2013-6-9"
}
```

### 3) Instructions Estimation
Given information like port, cargoes being loaded/discharged, berth, hose connection and operation (Loading/Discharging), the API will output the instructions. In the case where features like berth of connection, the API will use the remaining features to make an estimate.
<br>
Input:
``` 
 POST /instructions
{
  "Port": "Kawasaki",
  "Cargoes": [
    "Arabian Heavy", "Arabian Light"
  ],
  "Berth": "Sea Berth Dolphin",
  "Connection": "",
  "Operation": "Discharging"
}
```
Output:
```
[
    {
    "Labels": "Cargo Discharge Operation And Cow Operation",
    "Instructions": "Follow sequences on hourly stages and completed of each stage attached to the present plan"
    }, ... ...
]
```
### 4) Nomination Similarity
Given vessel, vol in BBLS and API of the cargoes in the same order, and the number of loading ports, the API will output similar nomination and stowage plans of past voyages for reference.
<br>
Input: 
``` 
 POST /nomination
{
  "Vessel": "Kazusa",
  "Vol": [
    480000, 530000, 490000, 550000
  ],
  "API": [
    34.0, 59.8, 29.9,40.5
  ],
  "LoadingPortsCount": 4
}
```

Output:
```
{
    "1": {
        "Vessel": "Gassan",
        "Voyage": 45,
        "similarity": 0.9556114285,
        "Nomination": {
            "Deodorized Field Condensate": {
                "Vol (BBLS)": 500000.0,
                "Max Tol": 0.05,
                "Min Tol": 0.05
            },
            "Qatar Land": {
                "Vol (BBLS)": 500000.0,
                "Max Tol": 0.05,
                "Min Tol": 0.05
            } ... ...
        },
        "Stowage": {
            "SP": {
                "Cargo": "Arabian Light",
                "Vol (BBLS)": 24001.0,
                "Weight (MT)": 3265.0
            },
            "5P": {
                "Cargo": "Qatar Land",
                "Vol (BBLS)": 88359.0,
                "Weight (MT)": 11477.0
            },
            ... ...
            "2S": {
                "Cargo": "Arabian Light",
                "Vol (BBLS)": 123637.0,
                "Weight (MT)": 16820.0
            },
            "1S": {
                "Cargo": "Deodorized Field Condensate",
                "Vol (BBLS)": 125971.0,
                "Weight (MT)": 14788.0
            }
        }
    }, ...
 }
```
