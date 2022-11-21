Setup 
- Python API
	- Tested on python > 3.6x
	- pip install fastapi uvicorn databases asyncpg aiottp httpx
- AMPL
	- pip install amplpy
	- Ensure AMPL folder in search path
- Postgresql
	- Modify DATABASE_URL (line 52) in main.py 
	- "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
        - in the format: username:password@IP:port/databaseName

Startup
- Run "uvicorn main:app --reload --host 0.0.0.0 --port 8000" in terminal 

Main APIs
- /new_loadable
	- Generate loadable plan
	- Sample usage in run_api.py
	- Input: loadableStudy.json
	- Output:
		- {'message': Error_messages}
		- {'processId':str(uuid), 'status':4/5, 'result':None}
	- Steps:
		- Generate processId
		- Save to DB
		- Get vessel info via API or FILE
			- Get from API
			- Get from FILE if API failed 
		- Return message if vessel info is not available
		- Combine the two jsons and start to generate loadable in background 
			- Run AMPL to generate plan
			- Update feedback via AO API
                - Send feedback via AO API
		- Return processId, status and result

        
- /status
	- Check the status
        - Sample usage in run_api_status.py
        - Input: {'processId':str(uuid)}
	- Output: 
		- {'processId':str(uuid), 'status':4, 'result':None}
		- {'processId':str(uuid), 'status':5, 'result':plan}
		- plan contains loadableStudyId, vesselId, voyageId and:
			- loading/unloading: operation to be done at each port
			- shipStatus: weight in vessel in arrival/departure conditions
			- message: Warning/Error
			- See obj2.json for example
	