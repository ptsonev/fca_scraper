RESULTS_PER_PAGE = 20

PAGINATION_URL = 'https://register.fca.org.uk/s/sfsites/aura?r={page}&other.ShPo_LEX_Reg_Search.getFirmDetails=1'
DETAILS_URL = 'https://register.fca.org.uk/s/sfsites/aura?r=0&other.ShPo_LEX_Reg_FirmDetail.initMethod=1&other.ShPo_LEX_Reg_Utility.GetGADetails=2&ui-self-service-components-profileMenu.ProfileMenu.getProfileMenuResponse=1'

MESSAGE = {

    "actions": [{
        "id": "7452;a",
        "descriptor": "apex://ShPo_LEX_Reg_SearchController/ACTION$getFirmDetails",
        "callingDescriptor": "markup://c:ShPo_LEX_Reg_SearchContainer",
        "params": {
            "searchValues": "",
            "pageSize": str(RESULTS_PER_PAGE),
            "pageNo": "1",
            "typeOfSearch": "Companies",
            "location": {
                "longitude": None,
                "latitude": None
            },
            "orderBy": "status",
            "sectorCriteria": " includes ('Investment','Pensions','Mortgage')",
            "hideUnauthFirm": True,
            "hideIntroARVal": False,
            "investmentTypes": []
        },
        "storable": True
    }
    ]
}

CONTEXT = {
    "mode": "PROD",
    "fwuid": "MDM0c01pMVUtd244bVVLc2VRYzQ2UWRkdk8xRWxIam5GeGw0LU1mRHRYQ3cyNDYuMTUuNS0zLjAuNA",
    "app": "siteforce:communityApp",
    "loaded": {
        "APPLICATION@markup://siteforce:communityApp": "_0uyRlc-Hz-jy1e6OwrFdg",
        "COMPONENT@markup://instrumentation:o11ySecondaryLoader": "Cpu-nBuFEwwbtqFxYd7Qhw"
    },
    "dn": [],
    "globals": {},
    "uad": False
}

DETAILS_MESSAGE = {
    "actions": [{
            "id": "1;a",
            "descriptor": "apex://ShPo_LEX_Reg_FirmDetailController/ACTION$initMethod",
            "callingDescriptor": "markup://c:ShPo_LEX_Reg_FirmDetails",
            "params": {
                "orgId": ""
            }
        }
    ]
}
