This is a basic set of instructions so that you can run the server on your local machine. 

WINDOWS:
1. Navigate to TestServer/Django and make sure you're running python3.6.
2. Run "python3 manage.py makemigrations" to register any changes that have been made to the database.
3. Run "python3 manage.py migrate" and commit these changes to the server. 
4. Now we can run the server. Run "python3 manage.py runserver" to get the server up and running. 
5. Navigate to "127.0.0.1:8000/eos/" and you should see the home page of the TestServer.
6. From here, you should be able to Upload a Test using the button in the top right, and run that test using the Run button. 
7. If you see "Invalid Script" that means that the Server was either unable to import the script or you are running the script in Debug mode.
    (To change from Debug to Production, just change the "production" value to True.)
8. Any other issues with the Server will be recorded in the Terminal and you should be able to see the root of the problem there. 