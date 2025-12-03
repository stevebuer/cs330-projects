#!/usr/bin/env python3
"""
VoIP.ms SMS notification module for DX alerts
Sends SMS via VoIP.ms REST API
"""

import os
import sys
import requests
from urllib.parse import urlencode

# VoIP.ms API Configuration
VOIPMS_API_URL = "https://voip.ms/api/v1/rest.php"

def test_api_connection(api_user=None, api_password=None):
    """
    Test VoIP.ms API connectivity and authentication
    
    Args:
        api_user (str): VoIP.ms API username (or set VOIPMS_API_USER env var)
        api_password (str): VoIP.ms API password (or set VOIPMS_API_PASSWORD env var)
    
    Returns:
        dict: Response with status, message, and account info if successful
    """
    # Get credentials from env vars if not provided
    if not api_user:
        api_user = os.getenv('VOIPMS_API_USER')
    if not api_password:
        api_password = os.getenv('VOIPMS_API_PASSWORD')
    
    if not api_user or not api_password:
        return {
            'status': 'error',
            'message': 'API credentials not provided. Set VOIPMS_API_USER and VOIPMS_API_PASSWORD'
        }
    
    # Use getBalance method to test connection and auth
    params = {
        'api_username': api_user,
        'api_password': api_password,
        'method': 'getBalance'
    }
    
    try:
        response = requests.get(VOIPMS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('status') == 'success':
            balance = result.get('balance', {})
            return {
                'status': 'success',
                'message': 'API connection successful',
                'balance': balance.get('current_balance', 'N/A'),
                'timestamp': balance.get('timestamp', 'N/A')
            }
        else:
            return {
                'status': 'error',
                'message': f"API authentication failed: {result.get('status', 'unknown error')}"
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f"Connection failed: {str(e)}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Unexpected error: {str(e)}"
        }


def send_sms(did, destination, message, api_user=None, api_password=None):
    """
    Send SMS via VoIP.ms API
    
    Args:
        did (str): Your VoIP.ms DID (phone number) to send from
        destination (str): Destination phone number (10 digits for US/Canada)
        message (str): Message content (max 160 chars per segment)
        api_user (str): VoIP.ms API username (or set VOIPMS_API_USER env var)
        api_password (str): VoIP.ms API password (or set VOIPMS_API_PASSWORD env var)
    
    Returns:
        dict: Response from API with status and message
    """
    # Get credentials from env vars if not provided
    if not api_user:
        api_user = os.getenv('VOIPMS_API_USER')
    if not api_password:
        api_password = os.getenv('VOIPMS_API_PASSWORD')
    
    if not api_user or not api_password:
        return {
            'status': 'error',
            'message': 'API credentials not provided. Set VOIPMS_API_USER and VOIPMS_API_PASSWORD'
        }
    
    # Build API request
    params = {
        'api_username': api_user,
        'api_password': api_password,
        'method': 'sendSMS',
        'did': did,
        'dst': destination,
        'message': message
    }
    
    try:
        response = requests.get(VOIPMS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('status') == 'success':
            return {
                'status': 'success',
                'message': 'SMS sent successfully',
                'sms_id': result.get('sms')
            }
        else:
            return {
                'status': 'error',
                'message': f"API error: {result.get('status', 'unknown error')}"
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Unexpected error: {str(e)}"
        }


def main():
    """Command line interface for sending SMS"""
    # Check for test mode
    if len(sys.argv) == 2 and sys.argv[1] in ['test', '--test', '-t']:
        print("Testing VoIP.ms API connection...")
        result = test_api_connection()
        
        if result['status'] == 'success':
            print(f"✓ {result['message']}")
            print(f"  Account Balance: ${result['balance']}")
            print(f"  Timestamp: {result['timestamp']}")
            sys.exit(0)
        else:
            print(f"✗ {result['message']}", file=sys.stderr)
            sys.exit(1)
    
    # Regular SMS sending mode
    if len(sys.argv) < 4:
        print("Usage: voipms_sms.py <did> <destination> <message>")
        print("       voipms_sms.py test  (test API connection)")
        print("\nEnvironment variables required:")
        print("  VOIPMS_API_USER     - Your VoIP.ms API username")
        print("  VOIPMS_API_PASSWORD - Your VoIP.ms API password")
        print("\nExamples:")
        print("  voipms_sms.py test")
        print("  voipms_sms.py 2065551234 2065559876 '10m FM is open!'")
        sys.exit(1)
    
    did = sys.argv[1]
    destination = sys.argv[2]
    message = sys.argv[3]
    
    print(f"Sending SMS from {did} to {destination}...")
    result = send_sms(did, destination, message)
    
    if result['status'] == 'success':
        print(f"✓ {result['message']}")
        if 'sms_id' in result:
            print(f"  SMS ID: {result['sms_id']}")
        sys.exit(0)
    else:
        print(f"✗ {result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
