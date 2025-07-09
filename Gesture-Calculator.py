import cv2
from cvzone.HandTrackingModule import HandDetector
import time

# Define a Button class to manage drawing and interaction
class button:
    def __init__(self, pos, wid, height, text):
        self.pos = pos          # Button position (top-left corner)
        self.wid = wid          # Width of the button
        self.height = height    # Height of the button
        self.text = text        # Label shown on the button

    def draw(self, img, clicked=False):
        # Button turns green when pressed, white by default
        color = (255, 255, 255) if not clicked else (0, 255, 0)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.wid, self.pos[1] + self.height), color, cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.wid, self.pos[1] + self.height), (50, 50, 50), 3)
        cv2.putText(img, self.text, (self.pos[0] + 20, self.pos[1] + int(self.height / 2) + 10),
                    cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 50), 2)

    def checkClick(self, x, y):
        # Determines whether a given point is inside the button area
        if self.pos[0] < x < self.pos[0] + self.wid and \
           self.pos[1] < y < self.pos[1] + self.height:
            return True
        else:
            return False

# Start the webcam feed
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width of the frame
cap.set(4, 720)   # Set height of the frame

# Initialize the hand detector with medium confidence and up to two hands
detector = HandDetector(detectionCon=0.5, maxHands=2)

# Define the layout of the calculator buttons (excluding "Del")
buttonListValues = [['7','8','9','*'],
                    ['4','5','6','-'],
                    ['1','2','3','+'],
                    ['.','0','=','/'],
                    ['','','','']]

# Create all the buttons from the layout
buttonList = []
for i in range(4):      # For each column
    for j in range(5):  # For each row
        xpos = i * 100 + 650  # Horizontal positioning
        ypos = j * 100 + 150  # Vertical positioning
        val = buttonListValues[j][i]
        if val != '':
            buttonList.append(button((xpos, ypos), 100, 100, val))

# Add a large 'Del' button to remove the last character from the equation
delButton = button((1055, 50), 100, 100, 'Del')

# Initialize variables for storing input and click tracking
myEquation = ''           # Expression currently being written
delayCounter = 0          # Optional delay mechanism (unused here)
clickedButtons = []       # List to store recently pressed buttons
clickTime = 0             # Timestamp of the last button press

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Flip image for mirror effect (more natural for interaction)

    # Detect any visible hands in the frame
    hands, img = detector.findHands(img)

    # Draw the output display area for the equation
    cv2.rectangle(img, (650, 50), (1050, 150), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(img, (650, 50), (1050, 150), (50, 50, 50), 3)

    # Highlight 'Del' button if recently pressed
    isDelClicked = any(idx == -1 and time.time() - t < 0.2 for idx, t in clickedButtons)
    delButton.draw(img, clicked=isDelClicked)

    # Draw all calculator buttons with appropriate highlights
    for i, btn in enumerate(buttonList):
        isClicked = any(i == idx and time.time() - t < 0.2 for idx, t in clickedButtons)
        btn.draw(img, clicked=isClicked)

    # Remove button press records that are older than 0.2 seconds
    clickedButtons = [(i, t) for i, t in clickedButtons if time.time() - t < 0.2]

    # If any hand is detected
    if hands:
        lmList = hands[0]['lmList']       # Get landmark positions
        p1 = lmList[8][:2]                # Tip of the index finger
        p2 = lmList[12][:2]               # Tip of the middle finger
        length, info, img = detector.findDistance(p1, p2, img)
        x, y = lmList[8][:2]              # Index finger tip coordinates

        # Consider a click only when fingers are close and last click was a while ago
        if length < 50 and time.time() - clickTime > 1.5:
            for i, btn in enumerate(buttonList):
                if btn.checkClick(x, y):  # If a button was clicked
                    myValue = btn.text
                    clickedButtons.append((i, time.time()))
                    clickTime = time.time()

                    if myValue == '=':    # When '=' is clicked, calculate the result
                        try:
                            myEquation = str(eval(myEquation))
                        except:
                            myEquation = 'Error'
                    elif myValue == 'C':  # Clear input if 'C' is pressed
                        myEquation = ''
                    else:                 # Add button's value to the equation
                        myEquation += myValue
                    delayCounter = 2

            # Handle the 'Del' button separately
            if delButton.checkClick(x, y):
                clickedButtons.append((-1, time.time()))
                clickTime = time.time()
                myEquation = myEquation[:-1]  # Remove the last character

    # Show the current input or result on screen
    cv2.putText(img, myEquation, (660, 120), cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)

    # Display the video feed with overlays
    cv2.imshow("Camera", img)
    if cv2.waitKey(1) == ord('q'):  # Press 'q' to exit
        break

# Cleanup after exiting the loop
cap.release()
cv2.destroyAllWindows()
print("Camera closed.")
print("Program terminated.")
# The code implements a simple calculator using OpenCV and hand tracking.
# It allows users to perform basic arithmetic operations by clicking buttons with their hands.
# The calculator supports addition, subtraction, multiplication, and division.
# It also includes a delete button to remove the last character from the equation.