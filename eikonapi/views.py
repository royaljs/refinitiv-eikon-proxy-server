from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import eikon as ek
from pandas import DataFrame
import json
from datetime import datetime
import os
import dateutil

#### SET EIKON APP KEY ####
ek.set_app_key('SET_APP_KEY_HERE')

##### NEWS #####
class NewsHeadlineView(APIView):
    """
    GET /news/headlines
    """
    def get(self, request):
        queryString = request.query_params.get('queryString', None)
        if queryString == None : return Response("queryString not provided. Please add queryString in query parameters.", status=400) # 필수 query parameter인 queryString 가 누락된 경우에 대한 응답
        count = request.query_params.get('count', None)
        if count != None : count = int(count) 
        else : count = 10
        dateFrom = request.query_params.get('dateFrom', None)
        dateTo = request.query_params.get('dateTo', None)
        # EikonError 처리
        try:
            result = ek.get_news_headlines(queryString, count, dateFrom, dateTo)
        except dateutil.parser._parser.ParserError:
            return Response('Invalid Date', status=400) 
        except ek.eikonError.EikonError as err:
            return Response(str(err), status=400)    
        return Response(json.loads(result.to_json(orient='index', date_format='iso', date_unit='s')), status=200) #pandas dataframe 객체에 to_json 사용시 redundant quote 가 추가되므로 json.loads를 적용한다.
 
class NewsStoryView(APIView):
    """
    GET /news/stories
    """
    def get(self, request):
        storyId = request.query_params.get('storyId', None)
        if storyId == None : return Response("storyId not provided. Please add storyId in query parameters.", status=400) # 필수 query parameter인 storyId 가 누락된 경우에 대한 응답
        # EikonError 처리
        try:
            result = ek.get_news_story(storyId)
        except ek.eikonError.EikonError as err:
            return Response(str(err), status=400)
        return Response(result, status=200)


##### DATA #####
class DataView(APIView):
    """
    GET /data
    """
    def get(self, request):
        instruments = request.query_params.get('instruments', None).replace(" ", "").split(",")
        if instruments == None : return Response("instruments not provided. Please add instruments in query parameters.", status=400) # 필수 query parameter인 instruments 가 누락된 경우에 대한 응답
        fields = request.query_params.get('fields', None).replace(" ", "").split(",")
        if fields == None : return Response("fields not provided. Please add fields in query parameters.", status=400) # 필수 query parameter인 fields 가 누락된 경우에 대한 응답
        
        # EikonError 처리
        try:
            result = ek.get_data(instruments, fields)[0]
        except ek.eikonError.EikonError as err:
            return Response(str(err), status=400)
        return Response(json.loads(result.to_json(orient='index')), status=200) # get_data API 반환 값이 json이 아닌 tuple 형태여서 to_json을 사용하기 위해 [0] 인덱싱..  redundant quote 제거를 위해 json.loads 적용

class TimeSeriesDataView(APIView):
    """
    GET /data/timeseries
    """
    def get(self, request):
        instruments = request.query_params.get('instruments', None).replace(" ", "").split(",")
        if instruments == None : return Response("instruments not provided. Please add instruments in query parameters.", status=400) # 필수 query parameter인 instruments 가 누락된 경우에 대한 응답
        fields = request.query_params.get('fields', '*').replace(" ", "").split(",") 
        dateFrom = request.query_params.get('dateFrom', None)
        dateTo = request.query_params.get('dateTo', None)
        interval = request.query_params.get('interval', None)
        
        # Invalid RIC에 대한 응답
        try:
            result = ek.get_timeseries(instruments, start_date=dateFrom, end_date=dateTo, interval=interval)
        except ek.eikonError.EikonError as err:
            return Response(str(err), status=400)
        
        # 엑셀 파일 저장
        result.to_excel(f'{os.path.dirname(__file__)}\\test_dir\\{datetime.today().strftime("%Y%m%d%H%M%S")}_{instruments}.xlsx')

        #interval이 minute, hour, daily, weekly, monthly, quarterly, yearly인 경우 (tick이 아닌 경우)
        if interval != 'tick' :
            return Response(json.loads(result.to_json(orient='index', date_format='iso', date_unit='ms')), status=200) #pandas dataframe 객체에 to_json 사용시 redundant quote 가 추가되므로 json.loads를 적용한다.
        #interval이 tick인 경우 (이 경우 index인 시각이 중복되는 경우에 대한 처리가 필요함)
        elif interval == 'tick' :
            dictByColumns = result.apply(dict, axis=1) #column(VALUE, VOLUME)에 dictionary 적용
            result = dictByColumns.groupby(dictByColumns.index).apply(list) #index(시각) 기준으로 list 적용
            return Response(json.loads(result.to_json(orient='index', date_format='iso', date_unit='ms')), status=200) #pandas dataframe 객체에 to_json 사용시 redundant quote 가 추가되므로 json.loads를 적용한다.