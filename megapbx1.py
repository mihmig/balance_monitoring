import requests
import json
from datetime import datetime

sess = requests.Session()
credentials = {"u": "inside@vats210601.megapbx.ru","p": "O0NcLpJLdF","r": False}
res = sess.post('https://vats210601.megapbx.ru/api/v2/login', json=credentials)
req = {
	"owner": "my",
	"start": "2023-09-17T21:00:00.000Z",
	"end": "2023-09-24T20:59:59.999Z",
	"CallType": "total",
	"search": {},
	"via": [],
	"thesaurus_id": [],
	"counted": 1,
	"notes": "true",
	"processMissed": True
}

records = sess.post('https://vats210601.megapbx.ru/api/v2/calls-history', json=req)
j = json.loads(records.text)
print(f"loaded records: {j['counts']['total']}")
#  j['calls'][0]
#  {'id': '0', 'uid': '1418962651', 'type': 'in', 'start': '2023-09-24T20:21:35.664Z', 'duration': 28, 'wait': 7, 'recordUrl': 'https://vats210601.megapbx.ru/api/v2/call-records/record/2023-09-24/2dedfa83-5382-4d87-a880-a4d831605c0d/79212991170_in_2023_09_24-23_21_43_79523077973_vu73.mp3', 'via': '79212991170', 'clientTelnum': '+79523077973', 'redirectTelnum': '79212991170', 'employeeId': 'inside', 'employeeRealName': 'inside'}
datetime.fromisoformat(j['calls'][0]['start'][:-1])

response = sess.get(j['calls'][0]['recordUrl'])
downloaded_file = response.content

j['calls'][0]

if response.status_code == 200:
    with open(j['calls'][0]['uid']+'.mp3', 'wb') as f:
        f.write(response.content)
