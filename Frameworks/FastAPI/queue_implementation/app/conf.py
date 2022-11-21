modules = {
    
        'LOADABLE':{
            "url": "https://cpdss-dev-ship.alphaorimarine.com/cpdss/api/ship/vessels/{vesselId}/voyages/{voyageId}/loadable-studies/{loadableStudyId}/loadable-study-status",
            "query": "body.get(modules[create_queue.process].get('infoId'))[0].get(create_queue.process.lower()+'StudyId') ",
            "infoId": "loadableStudyPortRotation",
            "info_name":"loadableStudyId",
            'info_type':'loadableStudyStatusId',
            'info_number':25},

        'DISCHARGE':{
            "url": "https://cpdss-dev-ship.alphaorimarine.com/cpdss/api/ship/vessels/{vesselId}/voyages/{voyageId}/discharge-studies/{dischargeStudyId}/discharge-study-status",
            "query": "body.get(modules[create_queue.process].get('infoId'))[0].get(create_queue.process.lower()+'StudyId') ",
            "infoId": 'dischargeStudyPortRotation',
            "info_name":"dischargeStudyId" ,
            'info_type':'loadableStudyStatusId',
            'info_number':25},

        'LOADING':{
            "url": "https://cpdss-dev-ship.alphaorimarine.com/cpdss/api/ship/vessels/{vesselId}/voyages/{voyageId}/loading-info/{infoId}/loading-info-status",
            "query": "body.get(modules[create_queue.process].get('infoId')).get(create_queue.process.lower()+'InfoId') ",
            "infoId": 'loadingInformation',
            "info_name":"infoId" ,
            'info_type':'loadingInfoStatusId',
            'info_number':21},

        'DISCHARGING':{
            "url": "https://cpdss-dev-ship.alphaorimarine.com/cpdss/api/ship/vessels/{vesselId}/voyages/{voyageId}/discharging-info/{infoId}/discharging-info-status",
            "query": "body.get(modules[create_queue.process].get('infoId')).get('dischargeInfoId') ",
            "infoId": 'dischargeInformation',
            "info_name":"infoId",
            'info_type':'dischargingInfoStatusId',
            'info_number':21},     
        }
