# refinitiv-eikon-proxy-server
A project of Refinitiv Eikon Data Proxy server for cooperation with team members

# 서비스 소개
각종 금융 데이터를 수집하려는 목적으로 Reuter 사의 Refinitiv Eikon 서비스를 사용한다.

EikonDataService 서비스는 공식 제공되는 Eikon Data API를 통해 금융 데이터를 요청하는 프록시 서비스를 지원한다.

Eikon Data API를 통해 수집한 금융 데이터를 RDB에 저장하고, RDB에 존재하는 데이터를 요청한 경우 Eikon Data API 대신 RDB에서 데이터를 조회하는 기능은 추후 구현 예정.

# 환경설정
Reuter사의 Refinitiv Eikon Data API는 파이썬 라이브러리로 제공된다.

이 브랜치의 eikon 데이터 프록시 서버는 파이썬 프레임워크인 Django와 DjangoRestFramework를 토대로 구현되어있으므로 기본적인 파이썬 개발 환경이 필요하다.

또한 Eikon Data API는 Eikon 데스크탑 앱이 켜진 상태에서만 동작하기 때문에 Eikon 데스크탑 앱이 설치되어 있어야한다. 

해당 앱은 Windows에만 제공되므로 OS도 Windows나 MacOS를 사용한다.

- OS: Windows
- Eikon 데스크탑 앱: 공식 홈페이지에서 다운로드 및 설치
- 파이썬 버전: python 3.9
- 파이썬 패키지 매니저: pip3


```sh
$ pip3 install pandas eikon django djangorestframework
```

주의사항: python 3.x 버전에서만 지원되는 라이브러리는 pip로 설치시 정상동작하지 않을 수 있으므로 pip3로 설치한다.

# 서버 실행

```sh
$ cd EikonDataService
$ python manage.py runserver $IP:$PORT
```

# 서비스 구성 및 API 호출 예시
이 중개서버는 Eikon Data API에 4가지 핵심 조회 API인 get_data, get_timeseries, get_news_headlines, get_news_story에 대한 프록시 서비스를 제공한다.

모든 API는 GET HTTP 요청을 통해 호출할 수 있으며, 요청에 필요한 인자는 query parameter로 입력한다. (ex. /eikon/news/headlines?queryString=KOREA&count=3&dateFrom=2020-01-20T15:04:05&dateTo=2021-01-25T15:04:05)
뉴스 스토리 조회 API를 제외한 모든 API는 JSON 형식의 응답을 준다.

### GET /eikon/data
금융 종목의 일반적 정보를 요청한다.

여러 종목 및 항목을 요청할 경우 query parameter에 배열로 입력하면 된다.

#### Request
| query parameter (Type/Format)           | Description                          |
| ---------------                         | ------------------------------------------------ |
| instruments (string/list of string) required    | 종목코드(RIC 코드/ticker) ex) IBM(IBM), T(AT&T), 005930.KS (삼성전자)     |
| fields (string/list of string) required         | 조회할 데이터 항목 ex) TR.PriceClose, TR.IPODate                          |

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

#### Request
| query parameter (Type/Format)               | Description                          |
| ---------------                             | ------------------------------------------------ |
| instruments (string/list of string) required        | 종목코드(RIC 코드/ticker) ex) IBM(IBM), T(AT&T), 005930.KS (삼성전자)     |
| fields (string/list of string) required             | 조회할 데이터 항목. TIMESTAMP, VALUE, VOLUME, HIGH, LOW, OPEN, CLOSE, COUNT 만 가능                         |
| dateFrom (datetime/YYYY-MM-DDThh:mm:ss) optional    | 조회의 시작일 ex)  2020-01-20T15:04:05   |
| dateTo (datetime/YYYY-MM-DDThh:mm:ss) optional      | 조회의 종료일 ex)  2021-01-20T15:04:05   |
| interval (string) optional                          | 조회할 시간 간격. tick, minute, hour, daily, weekly, monthly, quarterly, yearly이 가능. 기본값은 daily     |

#### Response
요청한 시계열 데이터에 대해 JSON 형태로 응답하며, 서버 디렉토리(현재 EikonDataService/eikonapi/test_dir 경로)에 해당 시계열 데이터를 엑셀 파일 (요청시각_종목명.xlsx)로 저장한다.

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

### GET /eikon/news/headlines
특정 기간의 뉴스 헤드라인을 요청한다.

응답으로 뉴스 헤드라인 텍스트와 뉴스ID(storyID) 를 반환하며, storyId를 통해 뉴스 내용을 조회할 수 있다.

#### Request
| query parameter (Type/Format)               | Description                          |
| ---------------                             | ------------------------------------------------ |
| queryString (string/list of string) required        | 검색어 ex) "Korea", "Topic:TOPALL and Language:LEN"     |
| count (integer) optional             | 조회할 뉴스 건수. 1-100의 값만 가능                         |
| dateFrom (datetime/YYYY-MM-DDThh:mm:ss) optional    | 조회의 시작일 ex)  2020-01-20T15:04:05   |
| dateTo (datetime/YYYY-MM-DDThh:mm:ss) optional      | 조회의 종료일 ex)  2021-01-20T15:04:05   |

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
뉴스 내용을 요청한다.

query parameter로 storyId를 입력한다.

응답으로 html 텍스트 형식의 뉴스 내용을 반환한다.

#### Request
| query parameter (Type/Format)               | Description                          |
| ---------------                             | ------------------------------------------------ |
| storyId (string) required        | 뉴스 헤드라인 조회 API를 통해 얻은 뉴스 ID ex) urn:newsml:reuters.com:20210125:nFtn6wlQhz:1     |

#### Response
```json
"<div class=\"storyContent\" lang=\"en\"><style type=\"text/css\">.storyContent * {border-color:inherit !important;outline-color:inherit !important;}</style><p>The EU-China deal that gives Beijing too little to lose</p><p>Hello from Brussels. Following the EU’s investment deal with China — of which more below — it’s the US’s turn to provoke a cry of ...(<a href=\"https://www.ft.com/cms/s/cfe4b5a3-1f64-4dfd-9a5b-133233a17ae6.html?FTCamp=engage/CAPI/app/Channel_Refinitiv//B2B\" data-type=\"url\" class=\"tr-link\" translate=\"no\">Full Story</a>)</p><p>© The Financial Times Limited 2021</p></div>"
```


# 로그
EikonDataService/logs 디렉토리의 info.log 및 error.log 파일을 통해 Request-Response 및 각종 에러 로그를 확인할 수 있다.