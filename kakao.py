from bs4 import BeautifulSoup
from dataclasses import dataclass
import requests
import json
MAX = 5
MMAX = 10000
INF = 99999
AVG = 3
problemURL = "https://grepp-cloudfront.s3.ap-northeast-2.amazonaws.com/programmers_imgs/competition-imgs/2021kakao/problem1_day-1.json"
# 만약에 자전거를 빌려야하는데 자전거가 없다

# class
class truck:
    time: int = None
    y: int = None
    x: int = None
    idx: int = None

class pos:
    y: int = None
    x: int = None

class Simulate:
    status: str = None
    time: str = None
    failed_requests_count: str = None
    distance: str = None
    def __init__(self,status,time,failed_requests_count,distance):
        self.status = status
        self.time = time
        self.failed_requests_count = failed_requests_count
        self.distance = distance

class Land:
    sId : int
    eId : int
    time : int

idxM = [pos() for j in range(MAX*MAX)]
# static variable
# BASE URL
URL = 'https://kox947ka1a.execute-api.ap-northeast-2.amazonaws.com/prod/users'
dx = [1, 0, -1, 0]
dy = [0, 1, 0, -1]
mp = [[0 for i in range(MAX)] for j in range(MAX)]


def startAPI():
    headers = {
        'X-Auth-Token': '44a1628476646f2b19b8e0d54663382e',
        'Content-Type': 'application/json',
    }

    data = '{ "problem": 1 }'

    response = requests.post(
        'https://kox947ka1a.execute-api.ap-northeast-2.amazonaws.com/prod/users/start', headers=headers, data=data)
    #print(response)
    Auth_data = response.json()
    Auth_json = json.loads(json.dumps(Auth_data))
    Auth_key = Auth_json.get("auth_key")
    print(Auth_key)
    return Auth_key


def locationAPI(Auth_key):
    headers = {
        'Authorization': Auth_key,
        'Content-Type': 'application/json',
    }
    response = requests.get(URL+'/locations', headers=headers)
    loc_data = response.json()
    loc_json = json.loads(json.dumps(loc_data))
    location = loc_json.get("locations")

    #print(location)
    return location


def TrucksAPI(Auth_key):
    headers = {
        'Authorization': Auth_key,
        'Content-Type': 'application/json',
    }
    response = requests.get(URL+'/trucks', headers=headers)
    truck_data = response.json()
    truck_json = json.loads(json.dumps(truck_data))
    truck = truck_json.get("trucks")
    #print(truck)
    return truck


def DoNothing(time, y, x):
    return time+6, y, x

def mapId(N):
    # 새로 방향으로 올라가므로
    idx = 0
    for i in range(N):
        for j in range(N):
            mp[i][j] = idx
            idxM[idx].x = i
            idxM[idx].y = j
            idx = idx+1

def ScoreAPI(Auth_key):
    headers = {
        'Authorization': Auth_key,
        'Content-Type': 'application/json',
    }
    response = requests.get(URL+'/score', headers=headers)
    score_data = response.json()
    score_json = json.loads(json.dumps(score_data))
    score = score_json.get("score")
    return score
# 현제 시간 , 자전거가 놓여있는 table, 시작id, 끝id, 타는시간
def moveBicycle(time, timetable, start, end, dur):
    # 시작과 끝 좌표
    st = pos(idxM[start])
    ed = pos(idxM[end])
    if timetable[st.y][st.x][time] == 0:
        return timetable

def LandAPI():
    response = requests.get(problemURL)
    land_data = response.json()
    land_json = json.loads(json.dumps(land_data))
    land = land_json.get("")
    return land

def SimulateAPI(Auth_key,trucks,command):
    headers = {
        'Authorization': Auth_key,
        'Content-Type': 'application/json',
    }
    data = json.dumps(command)
    response = requests.put(URL+'/simulate', headers=headers, data=data)
    sim_data = response.json()
    sim_json = json.loads(json.dumps(sim_data))
    location = locationAPI(Auth_key)
    trucks= TrucksAPI(Auth_key)
    simulate = Simulate(
        sim_json.get('status'),
        sim_json.get('time'),
        sim_json.get('failed_requests_count'),
        sim_json.get('distance')
    )
    #print(location)
    return simulate.status
def move(fr = pos(),to = pos(),w = 0,id = 0):
    commandO = dict()           
    cmd = list()
    #상차
    if w > 0:
        for i in range(w):
            cmd.append(5)
    # X축 이동(이동 하려는 위치가 오른쪽에 있는 경우)
    if fr.x < to.x:
        for i in range(to.x - fr.x):
            cmd.append(2)
    # X축 이동(이동 하려는 위치가 왼쪽에 있는 경우)
    if fr.x > to.x:
        for i in range(fr.x - to.x):
            cmd.append(4)
    # Y축 이동(이동 하려는 위치가 위에 있는 경우)
    if fr.y < to.y:
        for i in range(to.y - fr.y):
            cmd.append(1)
    # Y축 이동(이동 하려는 위치가 아래에 있는 경우)
    if fr.y > to.y:
        for i in range(fr.y - to.y):
            cmd.append(3)    
    #하차하는 경우
    if w < 0:
        for i in range(-w):
            cmd.append(6)
    
    commandO["truck_id"] = id
    commandO["command"] = cmd
    return commandO
# ---Main---
# 알고리즘 1 => # 가장 적은 곳으로 이동 하면서 중간에 자전거가 avg보다 많을 경우 태워서 간다.

# 인증키
Auth_key = startAPI()


# # 빌리는 내역 
# land = LandAPI()

# mapId 설정
mapId(MAX)

# 시뮬
data = {'commands' : {}}
while 1:
    a_list = []
    # 위치 정보 
    location = locationAPI(Auth_key)
    # 트럭 위치 
    trucks= TrucksAPI(Auth_key)
    # 트럭 vst
    vstT = [0 for i in range(MAX*MAX)]
    # 위치 vst
    vst = [0 for i in range(MAX*MAX)]
    for i in range(MAX*MAX):
        id = i
        count = location[i].get('located_bikes_count')
        command = dict()
        truckId = 0
        diff = 0
        # 만약에 평균보다 많을 경우 상차
        if count > AVG:
            trucks = TrucksAPI(Auth_key)
            mn = INF
            for tr in trucks:
                if vstT[tr['id']] == True:
                    continue
                truckCount = tr['loaded_bikes_count']
                # 지정
                if mn > truckCount:
                    truckId = tr['id']
                    mn = truckCount
                    diff = count - AVG;
            vstT[truckId] = True
        # 평균 보다 적을 경우 하차
        elif count < AVG:
            mx = -1
            for tr in trucks:
                if vstT[tr['id']] == True:
                    continue
                truckCount = tr['loaded_bikes_count']
                # 지정
                if mx < truckCount:
                    truckId = tr['id']
                    mx = truckCount
                    diff = count - AVG
            vstT[truckId] = True
        #이동
        fr = pos()
        fr = idxM[trucks[truckId]['location_id']]
        to = pos()
        to = idxM[id] 
        if diff == 0:  
            continue
        command = move(fr,to,diff,truckId)
        a_list.append(command)
    data["commands"] = a_list
    if SimulateAPI(Auth_key,trucks,data) == "finished":
        break
# 스코어
print(ScoreAPI(Auth_key))

