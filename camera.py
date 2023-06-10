from roboflow import Roboflow
rf = Roboflow(api_key="6riPgDH2G6Wn2Lqa4MTC")
model = rf.workspace().project("ckure").version(4).model
response = model.predict("assets/Damages/10.jpg", confidence=40, overlap=30).json()


if not response['predictions']:
    max_confidence = "No prediction found!"
    max_confidence_damage = "No prediction found!"
else:
    print("Damage found!")
    confidences, damages = zip(*[(round(pred['confidence']*100, 2), pred['class']) for pred in response['predictions']])
    max_confidence_index = confidences.index(max(confidences))
    max_confidence = max(confidences)
    max_confidence_damage = damages[max_confidence_index]
print(f"{max_confidence}%\n{max_confidence_damage}")


