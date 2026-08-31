# import requests

# MAP_KEY = "2d303ba668e0a08119c1b2c215824098"

# # AOI = Area of Interest — jitna area cover karna hai
# # Format: west, south, east, north (bounding box)
# # Ye Nagpur, Maharashtra ke aas-paas ka area hai
# AOI_BBOX =  "68,6,97,36"

# SENSOR = "VIIRS_SNPP_NRT"   
# # VIIRS = satellite sensor ka naam
# # SNPP = Suomi National Polar-orbiting Partnership (satellite ka naam)
# # NRT = Near Real-Time — matlab data almost turant milta hai, kal ka ya purana nahi

# DAYS = 5  # pichle kitne din ka data chahiye

# url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SENSOR}/{AOI_BBOX}/{DAYS}"

# response = requests.get(url)
# print(response.text)


import requests

MAP_KEY = "2d303ba668e0a08119c1b2c215824098"

AOI_BBOX = "78.5,20.7,79.5,21.5"
SENSOR = "VIIRS_SNPP_NRT"
DAYS = 5

url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SENSOR}/{AOI_BBOX}/{DAYS}"

response = requests.get(url)

print("URL:", url.replace(MAP_KEY, "HIDDEN_KEY"))
print("Status Code:", response.status_code)
print("Response length:", len(response.text))

print("\nFIRST 1000 CHARACTERS:\n")
print(response.text[:1000])