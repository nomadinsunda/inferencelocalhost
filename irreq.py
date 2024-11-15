import requests
import time


def loginWebserver(login_url, username, password):
    
    login_data = {'username' : username, 'password' : password}
    login_response = requests.post(login_url, json=login_data)
    print('got response')
    print(login_response)
    print(login_response.json())
    temp = login_response.json()
    jwtoken = temp["token"]
    return jwtoken


def postInferenceResult(auth_token, inspection_result_url, data):

    hed = {'Authorization': 'Bearer ' + auth_token}
    
    response = requests.post(inspection_result_url, json=data, headers=hed)
    
    print(response)
    return response




