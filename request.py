import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

# api-endpoint
# URL = "http://maps.googleapis.com/maps/api/geocode/json"
URL = "https://www.bol.com/nl/order/basket/updateItemQuantity.html?id=62f39df773d6364d0fd93cc9&quantity=239"

# defining a params dict for the parameters to be sent to the API
PARAMS = {
    'id': '62f3a49373d6364d0fe2c453',
    'quantity': 500
}

# sending get request and saving the response as response object
r = requests.get(url=URL, params=PARAMS)

r_basket = requests.get(url='https://www.bol.com/nl/order/basket.html')
r_basket.text
r.text
# extracting data in json format
data = r.json()

# extracting latitude, longitude and formatted address
# of the first matching location
latitude = data['results'][0]['geometry']['location']['lat']
longitude = data['results'][0]['geometry']['location']['lng']
formatted_address = data['results'][0]['formatted_address']

# printing the output
print("Latitude:%s\nLongitude:%s\nFormatted Address:%s"
      % (latitude, longitude, formatted_address))

"report-uri https://cspreport.bol.com/report/b/14700  ; default-src https://tpc.googlesyndication.com https://www.bol.com ; connect-src https://*.adyen.com https://*.akstat.io https://*.doubleclick.net https://*.google-analytics.com https://*.google.com https://*.googlesyndication.com https://*.gstatic.com https://*.mpstat.us https://*.s-bol.com https://aai.bol.com https://api.bol.com https://c.go-mpulse.net https://chat1.bol.com https://chatr.bol.com https://fbstatic-a.akamaihd.net https://firefly.bol.com https://suggestions.bol.com https://www.bol.com ; font-src data: https://*.s-bol.com https://fonts.gstatic.com https://secure.ogone.com https://www.bol.com ; frame-src https://*.2mdn.net https://*.adyen.com https://*.akstat.io https://*.doubleclick.net https://*.mpstat.us https://*.safeframe.googlesyndication.com https://*.youtube-nocookie.com https://bolfelicitatie.b05-apps.nl https://chat1.bol.com https://chatr.bol.com https://info.bol.com https://platform.twitter.com https://s-static.ak.facebook.com https://secure.ogone.com https://tpc.googlesyndication.com https://view.publitas.com https://www.bol.com https://www.facebook.com https://www.google.com ; img-src blob: data: https://*.2mdn.net https://*.adyen.com https://*.akstat.io https://*.doubleclick.net https://*.google-analytics.com https://*.google.be https://*.google.nl https://*.krxd.net https://*.moatads.com https://*.mpstat.us https://*.s-bol.com https://adservice.google.be https://adservice.google.com https://adservice.google.nl https://bol.com https://bol.ugc.bazaarvoice.com https://cbks0.googleapis.com https://cbks1.googleapis.com https://csi.gstatic.com https://ds-aksb-a.akamaihd.net https://fbstatic-a.akamaihd.net https://img.youtube.com https://kbimages1-a.akamaihd.net https://khms0.googleapis.com https://khms1.googleapis.com https://m.bol.com https://maps.googleapis.com https://maps.gstatic.com https://mts0.googleapis.com https://mts1.googleapis.com https://pagead2.googlesyndication.com https://partner.bol.com https://photos-eu.bazaarvoice.com https://platform.twitter.com https://secure.ogone.com https://ssl.gstatic.com https://static.bol.com https://swa.bol.com https://syndication.twitter.com https://tpc.googlesyndication.com https://view.publitas.com https://weblog.bol.com https://www.bol.com https://www.facebook.com https://www.google.com https://www.googletagmanager.com https://www.ups.com ; media-src blob: https://*.kobo.com https://*.phononet.de https://*.s-bol.com https://bolfelicitatie.b05-apps.nl https://rovimusic.rovicorp.com https://static.bol.com https://www.bol.com ; object-src https://bolfelicitatie.b05-apps.nl https://st1.streamzilla.jet-stream.nl https://view.publitas.com https://www.bol.com ; script-src 'unsafe-eval' 'unsafe-inline' data: https://*.2mdn.net https://*.adyen.com https://*.doubleclick.net https://*.google-analytics.com https://*.krxd.net https://*.moatads.com https://*.s-bol.com https://*.youtube-nocookie.com https://aai.bol.com https://adservice.google.be https://adservice.google.com https://adservice.google.nl https://ajax.googleapis.com https://apis.google.com https://bol.com https://c.go-mpulse.net https://cbks0.googleapis.com https://cdn.ampproject.org https://cdn.syndication.twimg.com https://cdn.syndication.twitter.com https://chat1.bol.com https://connect.facebook.net https://d31qbv1cthcecs.cloudfront.net https://ds-aksb-a.akamaihd.net https://fbstatic-a.akamaihd.net https://firefly.bol.com https://maps.googleapis.com https://maps.gstatic.com https://mts0.googleapis.com https://mts1.googleapis.com https://pagead2.googlesyndication.com https://partner.bol.com https://partner.googleadservices.com https://platform.twitter.com https://s.ytimg.com https://secure.ogone.com https://static.bol.com https://tpc.googlesyndication.com https://translate.googleapis.com https://tu.tu-vms.com https://view.publitas.com https://weblog.bol.com https://www.bol.com https://www.google.com https://www.googletagmanager.com https://www.googletagservices.com https://www.gstatic.com ; style-src 'unsafe-inline' https://*.s-bol.com https://bol.com https://fonts.googleapis.com https://partner.bol.com https://platform.twitter.com https://secure.ogone.com https://static.bol.com https://view.publitas.com https://www.bol.com ; worker-src blob: https://www.bol.com ; frame-ancestors 'self'"
