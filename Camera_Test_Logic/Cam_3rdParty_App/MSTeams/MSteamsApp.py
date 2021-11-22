import os
from azure.communication.identity import CommunicationIdentityClient, CommunicationUserIdentifier

try:
   print("Azure Communication Services - Access Tokens Quickstart")
   # Quickstart code goes here
except Exception as ex:
   print("Exception:")
   print(ex)

   # This code demonstrates how to fetch your connection string
   # from an environment variable.
connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]

   # Instantiate the identity client
client = CommunicationIdentityClient.from_connection_string(connection_string)

identity = client.create_user()
print("\nCreated an identity with ID: " + identity.properties['id'])
token_result = client.get_token(identity, ["voip"])
expires_on = token_result.expires_on.strftime("%d/%m/%y %I:%M %S %p")
print("\nIssued an access token with 'voip' scope that expires at " + expires_on + ":")
print(token_result.token)