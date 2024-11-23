import os
import requests
from ozon.cookies_manager import get_headers
from ozon.waypoints_data import format_waypoints
from ozon.request_ati import create_request_body


def get_biddings_list(cookies, processed_bids):
    url = "https://tms.ozon.ru/graphql-decorator.lpp/gql"
    headers = get_headers(cookies)
    payload = {
        "operationName": "BiddingsList",
        "variables": {
            "filter": {
                "Limit": 40,
                "OnlyCurrentContractBids": False,
                "Status": ["InBidding"],
                "WayType": "Direct"
            }
        },
        "query": """query BiddingsList($filter: LotsInput!) {
                      Lots(filter: $filter) {
                        ID
                        Status
                        Procedure { Name }
                        TransportType { ID Name }
                        Route {
                          WayPoints {
                            Point { ID Name Address }
                          }
                        }
                      }
                    }"""
    }

    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    bids = response_data.get('data', {}).get('Lots', [])
    new_bid_ids = [bid['ID'] for bid in bids if bid['ID'] not in processed_bids]
    return new_bid_ids

def get_bidding_details(cookies, bidding_id):
    url = "https://tms.ozon.ru/graphql-decorator.lpp/gql"
    headers = get_headers(cookies)
    payload = {
        "operationName": "Bidding",
        "variables": {"biddingId": bidding_id},
        "query": """query Bidding($biddingId: Int!) {
                      LotByID(filter: {ID: $biddingId}) {
                        ID
                        BiddingDurationSeconds
                        CreatedAt
                        Status
                        TariffType
                        TransportType {
                          ID
                          Name
                          Capacity
                          Palletes
                          CapacityValue
                          Tonnage
                          Attributes {
                            ContainerValidation
                            TrailerValidation
                            __typename
                          }
                          __typename
                        }
                        Temperature {
                          ID
                          Name
                          __typename
                        }
                        Route {
                          WayPoints {
                            Actions
                            ArrivalAt
                            LoadingTimeMinutes
                            Point {
                              Name
                              Address
                              __typename
                            }
                            __typename
                          }
                          __typename
                        }
                        Currency
                        Procedure {
                          Name
                          __typename
                        }
                        ProcedureInfo {
                          ...ProcedureInfo
                          __typename
                        }
                        Description
                        Auction {
                          Countdown
                          __typename
                        }
                        Version
                        ApprovalCountdownSeconds
                        __typename
                      }
                    }
                    
                    fragment ProcedureInfo on ProcedureInfo {
                      ... on BiddingWithLimit {
                        __typename
                        Rank
                        BiddingStarted
                        StartPrice
                        ContractorLastBid {
                          Price
                          __typename
                        }
                      }
                      ... on DownBiddingWithStartPrice {
                        __typename
                        StartPrice
                        Step
                        LastBid {
                          Price
                          FromCurrentContractor
                          __typename
                        }
                      }
                      __typename
                    }"""
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json().get('data', {}).get('LotByID', {})
    
    return create_request_body(data)


