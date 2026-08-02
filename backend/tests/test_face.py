from ai.image.preprocess import load_image

img = load_image("test.jpg")

print(img.size)

img.save("cropped_face.jpg")

print("Done!")