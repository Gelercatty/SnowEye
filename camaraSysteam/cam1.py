import cv2

# URL of the H.264 network video stream
video_url = "rtsp://192.168.8.92/live_stream"

# Output file name
output_file = "output.h264"

# Open the video stream
cap = cv2.VideoCapture(video_url)

# Check if the video stream is successfully opened
if not cap.isOpened():
    print("Error opening video stream")
    exit()

# Get the video stream's properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(cv2.CAP_PROP_FRAME_WIDTH)

print(frame_height)

print(fps)

# Create the video writer
fourcc = cv2.VideoWriter_fourcc(*"H264")
out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

# Read and save frames from the video stream until 'q' is pressed
while True:
    # Read a frame from the video stream
    ret, frame = cap.read()

    if ret:
        # Display the frame
        cv2.imshow("Frame", frame)

        # Write the frame to the output file
        out.write(frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release the video capture and writer
cap.release()
out.release()

# Close all OpenCV windowsw
cv2.destroyAllWindows()
