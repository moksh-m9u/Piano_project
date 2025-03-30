import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector

pygame.midi.init()
midi_out = pygame.midi.Output(0)
midi_out.set_instrument(0)

video = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

notes = {
    "left": {
        "thumb": [62, 66, 69],
        "index": [64, 67, 71],
        "middle": [66, 69, 73],
        "ring": [67, 71, 74],
        "pinky": [69, 73, 76]
    },
    "right": {
        "thumb": [62, 66, 69],
        "index": [64, 67, 71],
        "middle": [66, 69, 73],
        "ring": [67, 71, 74],
        "pinky": [69, 73, 76]
    }
}

sustain = 2.0
prev_status = {side: {finger: 0 for finger in notes[side]} for side in notes}

def play_chord(chord):
    for note in chord:
        midi_out.note_on(note, 127)

def stop_chord(chord):
    time.sleep(sustain)
    for note in chord:
        midi_out.note_off(note, 127)

while True:
    ret, frame = video.read()
    if not ret:
        continue

    hands, frame = detector.findHands(frame, draw=True)
    if hands:
        for hand in hands:
            side = "left" if hand["type"] == "Left" else "right"
            status = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]
            for i, finger in enumerate(finger_names):
                if status[i] == 1 and prev_status[side][finger] == 0:
                    play_chord(notes[side][finger])
                elif status[i] == 0 and prev_status[side][finger] == 1:
                    threading.Thread(target=stop_chord, args=(notes[side][finger],), daemon=True).start()
                prev_status[side][finger] = status[i]
    else:
        for side in notes:
            for finger in notes[side]:
                threading.Thread(target=stop_chord, args=(notes[side][finger],), daemon=True).start()
        prev_status = {side: {finger: 0 for finger in notes[side]} for side in notes}

    cv2.imshow("MIDI Chords", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
pygame.midi.quit()
