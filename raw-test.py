import requests

def test_nobitex_token():

    token = 'your_token'
    
    token = token.strip()
    
    url = "https://apiv2.nobitex.ir/users/wallets/list"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print("Sending direct request to Nobitex...")
    response = requests.post(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == '__main__':
    test_nobitex_token()