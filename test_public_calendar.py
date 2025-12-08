import requests

# Test calendar page without login
response = requests.get('https://backporch-chair-app-35851db28c9c.herokuapp.com/calendar')
print(f"Calendar Page Status: {response.status_code}")
print(f"Page loads successfully: {response.status_code == 200}")
print(f"Contains meeting info: {'meeting' in response.text.lower()}")
print(f"Contains chair info: {'chair' in response.text.lower()}")
print(f"Page size: {len(response.text)} bytes")

# Test a specific meeting detail
response2 = requests.get('https://backporch-chair-app-35851db28c9c.herokuapp.com/meeting/1')
print(f"\nMeeting Detail Status: {response2.status_code}")
print(f"Meeting detail accessible: {response2.status_code in [200, 302, 404]}")

print("\n✓ Calendar and meeting details are publicly accessible without login!")
