# refinitiv-eikon-proxy-server
A project of Refinitiv Eikon Data Proxy server for cooperation with team members

# 서비스 소개
각종 금융 데이터를 수집하려는 목적으로 Thomson Reuter 사의 Refinitiv Eikon 서비스를 사용한다.  
EikonDataService 서비스는 공식 제공되는 Eikon Data API를 통해 금융 데이터를 요청하는 프록시 서비스를 지원한다.  
Eikon Data API를 통해 수집한 금융 데이터를 RDB에 저장하고, RDB에 존재하는 데이터를 요청한 경우 Eikon Data API 대신 RDB에서 데이터를 조회하는 기능은 추후 구현 예정.

# 환경 설정
Thomson Reuter사의 Refinitiv Eikon Data API는 파이썬 라이브러리로 제공된다.  
Eikon 데이터 프록시 서버는 파이썬 프레임워크인 Django와 DjangoRestFramework를 토대로 구현되어있으므로 기본적인 파이썬 개발 환경이 필요하다.  
또한 Eikon Data API는 Thomson Reuter Eikon 데스크탑 앱을 통해 작동하기 때문에 Thomson Reuter Eikon 데스크탑 앱이 설치/실행되어야한다.   
해당 앱은 Windows에만 제공되므로 OS도 Windows를 사용한다.

#### 설치 리스트
- **OS:** Windows
- **Thomson Reuter Eikon 데스크탑 앱:** 공식 홈페이지에서 다운로드 및 설치
- **파이썬 버전:** python 3.9
- **파이썬 패키지 매니저:** pip3

#### 설정 리스트
- **eikon app key 설정:** /EikonDataService/eikonapi/view.py의 ek.set_app_key() 인자에 Thomson Reuter Eikon 앱의 key generator에서 발급된 key값을 입력한다. (**단, key generator로 새로 발급하지 않는 이상 해당 코드는 수정하지 않아도 된다.**)

```sh
$ pip3 install pandas eikon django djangorestframework
```

주의사항: python 3.x 버전에서만 지원되는 라이브러리는 pip로 설치시 정상동작하지 않을 수 있으므로 pip3로 설치한다.

# 서버 실행

```sh
Thomson Reuter Eikon 데스크탑 앱을 실행하고 로그인한다.
$ cd EikonDataService
$ python manage.py runserver $IP:$PORT
```

# 서비스 구성 및 API 호출 예시
이 서버는 Eikon Data API에 4가지 핵심 조회 API인 get_data, get_timeseries, get_news_headlines, get_news_story에 대한 프록시 서비스를 제공한다.  
모든 API는 GET HTTP 요청을 통해 호출할 수 있으며, 요청에 필요한 인자는 query parameter로 입력한다. (ex. /eikon/news/headlines?queryString=KOREA&count=3&dateFrom=2020-01-20T15:04:05&dateTo=2021-01-25T15:04:05)  
뉴스 스토리 조회 API를 제외한 모든 API는 JSON 형식의 응답을 준다.

### GET /eikon/data
금융 종목의 일반적 정보를 요청한다.  
여러 종목 및 항목을 요청할 경우 query parameter에 배열로 입력하면 된다.

#### Request
| query parameter (Type/Format)           | Description                          |
| ---------------                         | ------------------------------------------------ |
| **instruments** (string/list of string) _required_   | 종목코드(RIC 코드/ticker) ex) IBM(IBM), T(AT&T), 005930.KS (삼성전자)     |
| **fields** (string/list of string) _required_      | 조회할 데이터 항목 ex) TR.PriceClose, TR.IPODate                          |

#### Response

```json
 {
    "0": "{ //Request instruments 인자로 적은 순서대로 index가 0, 1, 2, ... 순서로 발급된다.
        \"Instruments\": \"IBM\",
        \"IPO Date\": \"1915-11-11\", // Request fields 인자에 따라 key-value 데이터가 변한다.
        \"Price Close\": 119.97,
    }",
    "1": "{
        \"Instruments\": \"005930.KS\",
        \"IPO Date\": \"1975-06-11\",
        \"Price Close\": 83200.0,
    }",
    "2": "{
        \"Instruments\": \"T\",
        \"IPO Date\": \"1983-11-21\",
        \"Price Close\": 29.57,
    }",
}
```

### GET /eikon/data/timeseries
금융 종목의 시계열 데이터를 요청한다.  
여러 종목 및 항목을 요청할 경우 query parameter에 배열로 입력하면 된다.  
Eikon 정책상 조회간격(interval)이 1일 미만인 경우(minute, tick 등)에는 조회가능한 기간이 최대 1년으로 제한된다.  

#### Request
| query parameter (Type/Format)               | Description                          |
| ---------------                             | ------------------------------------------------ |
| **instruments** (string/list of string) _required_        | 종목코드(RIC 코드/ticker) ex) IBM(IBM), T(AT&T), 005930.KS (삼성전자)     |
| **fields** (string/list of string) _required_             | 조회할 데이터 항목. VALUE, VOLUME, HIGH, LOW, OPEN, CLOSE, COUNT 만 가능. 단, interval이 tick인 경우 VALUE와 VOLUME만 가능.                         |
| **dateFrom** (datetime/YYYY-MM-DDThh:mm:ss) _optional_    | 조회의 시작일 ex)  2020-01-20T15:04:05   |
| **dateTo** (datetime/YYYY-MM-DDThh:mm:ss) _optional_      | 조회의 종료일 ex)  2021-01-20T15:04:05   |
| **interval** (string) _optional_                          | 조회할 시간 간격. tick, minute, hour, daily, weekly, monthly, quarterly, yearly이 가능. 기본값은 daily      |


#### Response
요청한 시계열 데이터에 대해 시각(datetime)을 key로 하는 JSON 형태로 응답한다.  
단, 조회 interval이 tick인 경우 동일 시각에 체결 데이터가 존재하므로 시각을 
조회된 시계열 데이터는 서버 디렉토리(현재 EikonDataService/eikonapi/data/timeseries 경로)에 해당 시계열 데이터를 엑셀 파일 (요청시각_종목명.xlsx)로 저장된다.

##### 하나의 instruments를 요청한 경우
```json
 {
    "2020-01-21T00:00:00Z": "{ // 시각이 key로 발급된다.
        \"HIGH\": 139.35, // Request fields 인자에 따라 key-value 데이터가 변한다.
        \"LOW\": 137.6,
        \"OPEN\": 137.6,
        \"CLOSE\": 139.17,
        \"VOLUME\": 7244079,
    }",
    "2020-01-22T00:00:00Z": "{
        \"HIGH\": 145.79,
        \"LOW\": 142.55,
        \"OPEN\": 143.32,
        \"CLOSE\": 143.89,
        \"VOLUME\": 16470431,
    }",
}
```

##### 복수의 instruments를 요청한 경우
```json
 {
    "2020-01-21T00:00:00Z": "{ // 시각이 key로 발급된다.
        \"('IBM', 'HIGH')\": 139.35, // Request fields 인자에 따라 key-value 데이터가 변한다.
        \"('IBM', 'LOW')\": 137.6,
        \"('IBM', 'OPEN')\": 137.6,
        \"('IBM', 'CLOSE')\": 139.17,
        \"('IBM', 'VOLUME')\": 7244079,
        \"('T', 'HIGH')\": 38.64,
        \"('T', 'LOW')\": 38.18,
        \"('T', 'OPEN')\": 38.35,
        \"('T', 'CLOSE')\": 38.52,
        \"('T', 'VOLUME')\": 43754575,
    }",
    "2020-01-22T00:00:00Z": "{
        \"('IBM', 'HIGH')\": 145.79,
        \"('IBM', 'LOW')\": 142.55,
        \"('IBM', 'OPEN')\": 143.32,
        \"('IBM', 'CLOSE')\": 143.89,
        \"('IBM', 'VOLUME')\": 16470431,
        \"('T', 'HIGH')\": 39.14,
        \"('T', 'LOW')\": 38.64,
        \"('T', 'OPEN')\": 38.68,
        \"('T', 'CLOSE')\": 39.04,
        \"('T', 'VOLUME')\": 36134774,
    }",
}
```


##### interval이 tick인 경우
```json
{
    "2021-01-25T20:52:30.826Z": [ // 시각이 key로 발급되며, value는 tick JSON 데이터의 list이다.
        {
            "VALUE": 142.895,
            "VOLUME": 100.0
        },
        {
            "VALUE": 142.89,
            "VOLUME": 100.0
        },
        {
            "VALUE": 142.89,
            "VOLUME": 2.0
        },
    ],
    "2021-01-25T20:52:30.828Z": [
        {
            "VALUE": 142.89,
            "VOLUME": 198.0
        }
    ],
    "2021-01-25T20:52:30.829Z": [
        {
            "VALUE": 142.9,
            "VOLUME": 100.0
        }
    ],
    "2021-01-25T20:52:30.839Z": [
        {
            "VALUE": 142.9,
            "VOLUME": 100.0
        }
    ],
```


### GET /eikon/news/headlines
특정 기간의 뉴스 헤드라인을 요청한다.  
응답으로 뉴스 헤드라인 텍스트와 뉴스ID(storyID) 를 반환하며, storyId를 통해 뉴스 내용을 조회할 수 있다.

#### Request
| query parameter (Type/Format)               | Description                          |
| ---------------                             | ------------------------------------------------ |
| **queryString** (string/list of string) _required_        | 검색어 ex) "Korea", "Topic:TOPALL and Language:LEN"     |
| **count** (integer) _optional_             | 조회할 뉴스 건수. 1-100의 값만 가능                         |
| **dateFrom** (datetime/YYYY-MM-DDThh:mm:ss) _optional_    | 조회의 시작일 ex)  2020-01-20T15:04:05   |
| **dateTo** (datetime/YYYY-MM-DDThh:mm:ss) _optional_      | 조회의 종료일 ex)  2021-01-20T15:04:05   |

검색어에 해당하는 queryString에는 RIC, 종목명, 국가명, 연산자(AND, OR, NOT, IN, 괄호, 따옴표)를 사용할 수 있다.
Eikon API 문서에 따르면 RIC 코드 앞에 R prefix를 달면 검색 성능이 더 좋아진다고 한다. ex) R:MSFT.O


#### Response
```json
 {
    "2020-01-21T00:00:00Z": "{ // 시각이 key로 발급된다.
        \"versionCreated\": \"2021-01-25T12:31:07Z\",
        \"text\": \"Global Forecast-Fahrenheit\",
        \"storyId\": \"urn:newsml:reuters.com:20210125:nNRAe3pxzz:1\", // 이 storyId를 이용하여 뉴스 내용을 조회할 수 있다.
        \"sourceCode\": \"NS:ASSOPR\",
    }",
    "2020-01-22T00:00:00Z": "{
        \"versionCreated\": \"2021-01-25T12:11:08Z\",
        \"text\": \"Biden's Asia policy will be controversial - and that's a good thing\",
        \"storyId\": \"urn:newsml:reuters.com:20210125:nNRAe3l81t:1\",
        \"sourceCode\": \"NS:SOUTHC\",
    }",
}
```


### GET /eikon/news/stories
특정 뉴스 내용을 요청한다.  
query parameter로 storyId를 입력한다.  
응답으로 html 텍스트 형식의 뉴스 내용을 반환한다.

#### Request
| query parameter (Type/Format)               | Description                          |
| ---------------                             | ------------------------------------------------ |
| **storyId** (string) _required_        | 뉴스 헤드라인 조회 API를 통해 얻은 뉴스 ID. ex) urn:newsml:reuters.com:20210125:nFtn6wlQhz:1     |

#### Response

`
"<div class=\"storyContent\" lang=\"en\"><style type=\"text/css\">.storyContent * {border-color:inherit !important;outline-color:inherit !important;}</style><p>The EU-China deal that gives Beijing too little to lose</p><p>Hello from Brussels. Following the EU’s investment deal with China — of which more below — it’s the US’s turn to provoke a cry of ...(<a href=\"https://www.ft.com/cms/s/cfe4b5a3-1f64-4dfd-9a5b-133233a17ae6.html?FTCamp=engage/CAPI/app/Channel_Refinitiv//B2B\" data-type=\"url\" class=\"tr-link\" translate=\"no\">Full Story</a>)</p><p>© The Financial Times Limited 2021</p></div>"
`

# 로그
EikonDataService/logs 디렉토리의 info.log 및 error.log 파일을 통해 Request-Response 및 각종 에러 로그를 확인할 수 있다.