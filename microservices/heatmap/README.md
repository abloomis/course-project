# CSV -> Heatmap Generating Microservice

## About
This Microservice will take CSV data of head-to-head matchups and use it to generate a heatmap in the same table layout.

## API Documentation

### API Calls
There are four stages when using this microservice.
1. The CSV must be uploaded to the microservice's file receiving endpoint.
2. A request must be made to the microservice's heatmap endpoint.
3. The microservice's heatmap endpoint will respond to the request with a confirmation or error message.
4. If the request was successful, then the  microservice's heatmap endpoint will send the image file.

#### 1. CSV Upload
Connect to the python socket endpoint at 3.131.47.90:5555.  
Send a 1024-byte message containing "NameOfCSVFile\<SEPERATOR\>SizeOfFileInBytes".  
Then continuously send 4096-byte messages containing CSV data until the file has been sent completely.  

Example:
```python
HOST = '3.131.47.90'
UPLOAD_PORT = 5555
SEPERATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def pad_string(text, length=MESSAGE_SIZE, char=' '):
    return text.ljust(length, char)

def initUploadSocket():
    s = socket.socket()
    print(f"Connecting to {HOST}:{UPLOAD_PORT}")
    s.connect((HOST, UPLOAD_PORT))
    print(f"Connected")
    return s

def uploadFile(socket, requestFileName):
    fileSize = os.path.getsize(requestFileName)
    message = requestFileName + SEPERATOR + str(fileSize)
    message = pad_string(message)
    socket.send(message.encode())

    with open(requestFileName, "rb") as f:
        while True:
            # read 4kB from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            socket.sendall(bytes_read)

uploadSocket = initUploadSocket()
uploadFile(uploadSocket, "MyCSVData.csv")
uploadSocket.close()
```

#### 2. Request for Heatmap
Connect to the python socket endpoint at 3.131.47.90:5556.  
Send a 1024-byte message containing "NameOfCSVFile\<SEPERATOR\>ColorString".  
Note: ColorString can be empty, but \<SEPERATOR\> must be included.  

Example:
```python
HOST = '3.131.47.90'
REQUEST_PORT = 5556
SEPERATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def pad_string(text, length=MESSAGE_SIZE, char=' '):
    return text.ljust(length, char)

def initRequestSocket():
    s = socket.socket()
    print(f"Connecting to {HOST}:{REQUEST_PORT}")
    s.connect((HOST, REQUEST_PORT))
    print(f"Connected")
    return s

def requestHeatmap(socket, requestFileName, colorString):
    # Request that the server make a heatmap
    message = requestFileName + SEPERATOR + colorString
    message = pad_string(message)
    socket.send(message.encode())

requestSocket = initRequestSocket()
requestHeatmap(requestSocket, "MyCSVData.csv", "#00FF00 #FFFF00 #0000FF")
```

#### 3. Response/Status Code Reply
The microservice will reply with a 1024-byte message of the status of the request.
- If the request was confirmed, it will reply with a message of the format "00 Some success message".
- If there was an issue with the request, it will reply with a message of the format "## Some error message".

Example:
```python
def isReplySuccessful(socket):
    # Receive some confirmation back from service that it will generate heat map with these inputs
    reply = socket.recv(MESSAGE_SIZE).decode().strip()
    if reply[:2] != '00':
        print('Error: ' +  reply[3:])
        return False
    else:
        print('Request successful')
        return True

success = isReplySuccessful(requestSocket)
```

#### 4. Receive Image File
The microservice will send a 1024-byte message of the format "SomeFileName\<SEPERATOR\>ImageFileSizeInBytes" (the client doesn't need to use this image name).  
The microservice will then send 4096-byte messages containing image data until the file has been sent completely. The client should write these bytes to their own local file.  

Example:
```python
def receiveFile(socket, newFilename):
    received = socket.recv(MESSAGE_SIZE).decode()
    filename, filesize = received.split(SEPERATOR)

    with open(newFilename, "wb") as f:
        while True:
            # read 4kB from the socket (receive)
            bytes_read = socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
    return

if isReplySuccessful(requestSocket):
  receiveFile(requestSocket, "TheImageNameIWantLocally.png")
```

#### The entire flow of an example client application can be found in /Client/Heatmap_Client.py

### Input parameters
#### Data CSV
The input CSV must have the opponent names in the top row, and in the first column of each row.   
Each cell then represents the results from these opponents competing.  
The table should be square, though some cells may be empty.  

Examples of data input as spreadsheet and CSV files:  
<img width="613" alt="Screenshot 2025-05-19 at 10 14 45 AM" src="https://github.com/user-attachments/assets/e3915a29-46c6-496e-8df5-9a2740f31f95" />
<img width="384" alt="Screenshot 2025-05-19 at 11 46 41 AM" src="https://github.com/user-attachments/assets/78408e82-535b-4017-b1d5-b0f1d3b9d13c" />

##### Important input formatting requirements
- There should be no commas at the end of rows, or extra new lines after the last row containing data.
- Each cell should be in the format '#-#'. 
- Players who have not played each other should have '0-0' as their scores, rather than an empty cell.
- Player names should not have more than 25 characters.
- This microservice only supports tables of up to 50 players' results.

#### Color String
The color string controls what colors are in the resulting heatmap image.  
It must be a string containing three hex colors in the format "positiveResultColor mediumResultColor negativeResultColor".  
For example, the default color settings of green, yellow, and red, would be "#00FF00 #FFFF00 #FF0000".  
If an empty string is sent, the microservice will use the green, yellow, red color scheme.

### Result Heatmap

The resulting heatmap has the same table format as input data.  
Diagonal cells are displayed black, as players do not have scores against themselves.  
If the table has 10 or fewer players, then the scores will be printed in the cells. Larger tables will not have this information in the image. 

Example with 5 players and default coloring:  
![ReturnedImage01](https://github.com/user-attachments/assets/b23d054c-4363-4587-99eb-5d584fbad752)

Example with 50 players and custom coloring:  
![ReturnedImage03](https://github.com/user-attachments/assets/ab89e355-fef5-43ef-a9ab-35ae012d4875)

## UML Sequence Diagram
![Blank diagram (1)](https://github.com/user-attachments/assets/408c9af6-9855-4c7f-a9c2-3fa5362a65f9)


