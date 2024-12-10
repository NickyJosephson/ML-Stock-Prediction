import requests
import pandas as pd
import time

# Base URL for Yahoo Finance API
# BASE_URL = "https://finance.yahoo.com/xhr/ncp?location=US&queryRef=topicsDetailFeed&serviceKey=ncp_fin&lang=en-US&region=US"
BASE_URL = "https://finance.yahoo.com/xhr/ncp?location=US&queryRef=homeNewsStreamNeo&serviceKey=ncp_fin&listName=home-news-stream&lang=en-US&region=US"
SECOND_URL = "https://finance.yahoo.com/xhr/ncp?location=US&queryRef=topicsDetailFeed&serviceKey=ncp_fin&lang=en-US&region=US"
BASE_PAYLOAD = {"serviceConfig":{"imageTags":["168x126|1|80","168x126|2|80"],"pageOffset":0},"session":{"consent":{"allowContentPersonalization":True,"allowCrossDeviceMapping":True,"allowFirstPartyAds":True,"allowSellPersonalInfo":True,"canEmbedThirdPartyContent":True,"canSell":True,"consentedVendors":[],"allowAds":True,"allowOnlyLimitedAds":False,"rejectedAllConsent":False,"allowOnlyNonPersonalizedAds":False},"authed":"0","ynet":"0","ssl":"1","spdy":"0","ytee":"0","mode":"normal","tpConsent":True,"site":"finance","adblock":"0","bucket":["rocket_GA_desk_test-3-v1","uspubs-pbcloadingchange-ctrl","uspubs-iabenrich-ctrl","yf-qsp-no-dynamic-insights"],"colo":"bf1","device":"desktop","bot":"0","browser":"chrome","app":"unknown","ecma":"modern","environment":"prod","gdpr":False,"lang":"en-US","dir":"ltr","intl":"us","network":"broadband","os":"mac os x","partner":"none","region":"US","time":1732687687434,"tz":"America/New_York","usercountry":"US","rmp":"0","webview":"0","feature":["disableServiceRewrite","enableAnalystRatings","enableChartbeat","enableChatSupport","enableCompare","enableCompareConvertCurrency","enableConsentAndGTM","enableCrumbRefresh","enableCurrencyConverter","enableDockAddToFollowing","enableDockCondensedHeader","enableDockNeoOptoutLink","enableDockPortfolioControl","enableExperimentalDockModules","enableLazyQSP","enableLiveBlogStatus","enableLivePage","enableMarketsHub","enableMonetizedLandingPages","enableMultiQuote","enableNeoArticle","enableNeoAuthor","enableNeoBasicPFs","enableNeoGreen","enableNeoHouseCalcPage","enableNeoInvestmentIdea","enableNeoMortgageCalcPage","enableNeoOptOut","enableNeoPortfolioDetail","enableNeoQSPReportsLeaf","enableNeoResearchReport","enableNeoTopics","enablePersonalFinanceArticleReadMoreAlgo","enablePersonalFinanceNewsletterIntegration","enablePersonalFinanceZillowIntegration","enablePf2SubsSpotlight","enablePfLandingP2","enablePfPremium","enablePfStreaming","enablePinholeScreenshotOGForQuote","enablePlus","enablePortalStockStory","enableQSPChartEarnings","enableQSPChartNewShading","enableQSPChartRangeTooltips","enableQSPEarningsVsRev","enableQSPHistoryPlusDownload","enableQSPNavIcon","enableQuoteLookup","enableRecentQuotes","enableResearchHub","enableScreenerRedesign","enableSECFiling","enableSigninBeforeCheckout","enableSmartAssetMsgA","enableStockStoryPfPage","enableStockStoryTimeToBuy","enableSubSpotlight","enableTradeNow","enableUpgradeBadge","enableCompareFeatures","enableGenericHeatMap","enableL2L3AB","enableMarketsLeafHeatMap","enableQSPIndustryHeatmap","enableStatusBadge","enableRapidClientOnlyPageView","enableRocketOptIn"],"isDebug":False,"isForScreenshot":False,"isWebview":False,"theme":"light","pnrID":"","isError":False,"areAdsEnabled":True,"ccpa":{"warning":"","footerSequence":["terms_and_privacy","dashboard"],"links":{"dashboard":{"url":"https://guce.yahoo.com/privacy-dashboard?locale=en-US","label":"Privacy Dashboard","id":"privacy-link-dashboard"},"terms_and_privacy":{"multiurl":True,"label":"${terms_link}Terms${end_link} and ${privacy_link}Privacy Policy${end_link}","urls":{"terms_link":"https://guce.yahoo.com/terms?locale=en-US","privacy_link":"https://guce.yahoo.com/privacy-policy?locale=en-US"},"ids":{"terms_link":"privacy-link-terms-link","privacy_link":"privacy-link-privacy-link"}}}},"yrid":"4t1hu0tjkddq7","user":{"age":-2147483648,"crumb":"SD4kpwGx2OR","firstName":None,"gender":"","year":0}}}

# Headers to mimic a browser
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain;charset=UTF-8",
    "origin": "https://finance.yahoo.com",
    "referer": "https://finance.yahoo.com/topic/stock-market-news/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

# Function to fetch news data
def fetch_news(pagination_token=None, first=True):
    # Payload for the request
    payload =   {

        "payload": {
            "gqlVariables": {
                "main": {
                    "pagination": {
                        "uuids": pagination_token
                    }
                }
            }
        },
        "serviceConfig": {
            "imageTags": [
                "168x126|1|80",
                "168x126|2|80"
            ],
            "pageOffset": 0
        },
        "session":{
        },
    
    }
    if first == True:
        payload = BASE_PAYLOAD
    # payload =  {
    #             "payload": {
    #         "gqlVariables": {
    #             "main": {
    #                 "pagination": {
    #     "uuids":"paginationString={\"streamPagination\":{\"uuids\":[{\"id\":\"6086b319-c7eb-397e-9e35-0915e52bf5ba\",\"type\":\"ymedia:type=story\"},{\"id\":\"7c0b2671-e4a9-307f-a7af-fae4daf1114d\",\"type\":\"ymedia:type=story\",\"metadata\":{\"is_pinned\":true}},{\"id\":\"864f5406-54e7-3832-8ae6-0ffdc6c82b0f\",\"type\":\"ymedia:type=story\"},{\"id\":\"7e4a89c9-c1ca-3497-bd8e-9a9a6274e43c\",\"type\":\"ymedia:type=story\"},{\"id\":\"95eb110d-daf4-317c-bf6b-3b685284501a\",\"type\":\"ymedia:type=story\"},{\"id\":\"09b9af73-6f7d-3d55-9f48-6e5ee88b60d9\",\"type\":\"ymedia:type=story\"},{\"id\":\"db5b2d75-eb8d-3149-a0ee-7566f964cb1d\",\"type\":\"ymedia:type=story\"},{\"id\":\"1a0dbfff-a062-396d-9ff1-7bff42accc0c\",\"type\":\"ymedia:type=story\",\"metadata\":{\"is_pinned\":true}},{\"id\":\"e1fadc05-4908-3726-95d3-83e5dca67841\",\"type\":\"ymedia:type=story\"},{\"id\":\"d07cf50c-f948-3f06-a857-a2f555ce28c8\",\"type\":\"ymedia:type=story\"},{\"id\":\"8b6b57da-4ebd-3c79-88c6-327a21617762\",\"type\":\"ymedia:type=story\"},{\"id\":\"b2aae989-b906-3408-937d-4b00386172ab\",\"type\":\"ymedia:type=story\"},{\"id\":\"22b5863a-b4c1-4f54-b1c9-3ba8861a2382\",\"type\":\"ymedia:type=story\"},{\"id\":\"bfa24372-4255-360b-babb-0696541d1869\",\"type\":\"ymedia:type=story\",\"metadata\":{\"is_pinned\":true}},{\"id\":\"2c998e1f-e135-41ac-99fe-3ce6a216023e\",\"type\":\"ymedia:type=story\"},{\"id\":\"c46cdfa6-99bc-3917-a9de-7d04f4ebd879\",\"type\":\"ymedia:type=story\"},{\"id\":\"05c76f40-0515-3b8f-a0e5-0d592bdb8c02\",\"type\":\"ymedia:type=story\"},{\"id\":\"fc353e04-6288-34c8-993a-7e4f02b617a7\",\"type\":\"ymedia:type=story\"},{\"id\":\"59eba1a4-27b9-3668-a55e-d587e45e8901\",\"type\":\"ymedia:type=story\"},{\"id\":\"8769ce18-fdfb-3a4f-a8d9-ed9e909991ea\",\"type\":\"ymedia:type=story\",\"metadata\":{\"is_pinned\":true}},{\"id\":\"bdde0fbb-a036-3910-a266-c80dc60141c7\",\"type\":\"ymedia:type=story\"},{\"id\":\"f1aa1774-8918-3cf7-a3fc-9da4ff25401f\",\"type\":\"ymedia:type=story\"},{\"id\":\"ea74580b-0e4a-3460-b158-30bcbb564a9d\",\"type\":\"ymedia:type=story\"},{\"id\":\"062d5f73-1fc9-36d3-ab29-c42145f7e4ae\",\"type\":\"ymedia:type=story\"},{\"id\":\"9b4232dc-afee-3fcf-93bd-7e1996827907\",\"type\":\"ymedia:type=story\"},{\"id\":\"9619d041-b194-376d-ac52-61f75989258d\",\"type\":\"ymedia:type=story\",\"metadata\":{\"is_pinned\":true}},{\"id\":\"dd152a03-acd6-3959-9166-eea9fa19b848\",\"type\":\"ymedia:type=story\"},{\"id\":\"210f5b40-4f2f-447d-ab5e-f3688e700e64\",\"type\":\"ymedia:type=story\"},{\"id\":\"c7dbbbcb-4e72-3d8f-9fe7-cf49a4376636\",\"type\":\"ymedia:type=story\"},{\"id\":\"9dc91d06-bce8-3afd-88fb-8cc87631b28a\",\"type\":\"ymedia:type=story\"},{\"id\":\"10f5db31-ef35-3ef4-8a5f-014726695e84\",\"type\":\"ymedia:type=story\"},{\"id\":\"4ad45099-186b-3d23-bd56-43c74defae55\",\"type\":\"ymedia:type=story\",\"metadata\":{\"is_pinned\":true}},{\"id\":\"7572d345-0145-39b4-8dec-b9e461966c2d\",\"type\":\"ymedia:type=story\"},{\"id\":\"d66bf9e3-3b5b-3b3a-b01d-a6f8946e490f\",\"type\":\"ymedia:type=story\"},{\"id\":\"db6d2ba3-450e-3205-aed3-7afc9e6f8492\",\"type\":\"ymedia:type=story\"},{\"id\":\"efe8c325-c7f9-3317-a556-fd6e9cce2146\",\"type\":\"ymedia:type=story\"},{\"id\":\"ffd2e747-91db-3dda-b7cc-fb0c3b74ee74\",\"type\":\"ymedia:type=story\"},{\"id\":\"5b897bc6-2083-3308-9709-bf5fed7dea29\",\"type\":\"ymedia:type=story\",\"metadata\":{\"is_pinned\":true}},{\"id\":\"51e72eaa-5875-3879-b644-ddb955b91696\",\"type\":\"ymedia:type=story\"},{\"id\":\"ee883c23-35ad-3664-b2af-1ec27dc7e7c4\",\"type\":\"ymedia:type=story\"}],\"seenHits\":[{\"id\":\"98498912-ecd9-38a0-8d9b-52b7f32b13f3\",\"type\":\"ymedia:type=story\",\"storyline\":[{\"id\":\"d9693945-739f-3375-b0b8-4eda7d476ed9\",\"type\":\"ymedia:type=story\"},{\"id\":\"288ab807-5f03-3dab-b76b-6e94ac4b0988\",\"type\":\"ymedia:type=story\"}]},{\"id\":\"3ab6ab17-0dcf-3062-b4aa-b7b98af2ddc9\",\"type\":\"ymedia:type=story\"},{\"id\":\"e4f96785-a026-3f9d-835c-4c9260e611f7\",\"type\":\"ymedia:type=story\"},{\"id\":\"72518fad-3f9c-31ff-adc0-06a91bb0397b\",\"type\":\"ymedia:type=story\"},{\"id\":\"6c5ff4e1-5b59-3ee2-a57b-a21325d90bd1\",\"type\":\"ymedia:type=story\"},{\"id\":\"ac690bab-d4c4-38a9-beae-605d548d5f45\",\"type\":\"ymedia:type=story\",\"storyline\":[{\"id\":\"18562944-4b39-31d1-95c2-e1caaab6fb15\",\"type\":\"ymedia:type=story\"},{\"id\":\"af0ce235-b4d6-3f2d-b81c-5ed16a0698ce\",\"type\":\"ymedia:type=story\"}],\"metadata\":{\"is_pinned\":true}},{\"id\":\"c4e32fa3-4b64-3ad5-a3d9-af47b6599d94\",\"type\":\"ymedia:type=story\"},{\"id\":\"ed126e89-dd8d-379a-9402-2a9a4f7d158f\",\"type\":\"ymedia:type=story\"},{\"id\":\"b0db4aa4-63ca-35d1-a8dc-391d2e48e10f\",\"type\":\"ymedia:type=story\",\"storyline\":[{\"id\":\"eda08e04-1db7-3217-849a-3fea5c27385a\",\"type\":\"ymedia:type=story\"}]},{\"id\":\"1e5dd51d-9c9b-3388-8818-f97f84f6f229\",\"type\":\"ymedia:type=story\"}],\"expId\":\"megastream_unified__en-US__finance__default__default__desktop__ga__main.finSwp25\",\"sessionId\":\"jarvis_dmeadjxyzzgxu_1732688830788\",\"lastVespaRequestTimestamp\":1732688830743,\"shouldGridLog\":true}}"
    #                 }
    #             }
    #         }
    #     },
    #             "serviceConfig": {
    #         "imageTags": [
    #             "168x126|1|80",
    #             "168x126|2|80"
    #         ],
    #         "pageOffset": 0
    #     },
    #     "session":{
    #     },
    # }

    try:
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Parse the response and extract articles
def parse_articles(data):
    articles = []
    if not data or "data" not in data:
        return articles
    
    stories = data.get("data", {}).get("main", {}).get("stream", [])
    for story in stories:
        article = {
            "title": story.get("content", {}).get("title", ""),
            # "url": story.get("content", {}).get("canonicalUrl", {}).get,
            "summary": story.get("content", {}).get("summary", ""),
            "published_at": story.get("content",{}).get("pubDate","")
        }
        articles.append(article)
    return articles

# Function to handle pagination and fetch more articles
def fetch_all_news():
    all_articles = []
    pagination_token = None
    first = True
    for _ in range(20):
        print("Fetching articles...")
        data = fetch_news(pagination_token, first)
        if not data:
            break

        articles = parse_articles(data)
        if not articles:
            print("No more articles found.")
            break
        
        all_articles.extend(articles)
        
        # Get the next pagination token
        pagination_token = data.get("data", {}).get("main", {}).get("pagination", {}).get("uuids", None)
        remaining = data.get("data", {}).get("main", {}).get("pagination", {}).get("remainingUuidCount", None)
        if not pagination_token:
            print("No more pages available.")
            break

        # Sleep to avoid overwhelming the server
        first = False
        time.sleep(2)

    return all_articles

# Save articles to a CSV file
def save_to_csv(articles, filename="financial_news.csv"):
    df = pd.DataFrame(articles)
    df.to_csv(filename, index=False)
    print(f"Saved {len(articles)} articles to {filename}.")

# Main function
if __name__ == "__main__":
    articles = fetch_all_news()
    if articles:
        save_to_csv(articles)