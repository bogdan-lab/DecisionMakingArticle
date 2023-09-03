import os
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# List of sample image URLs
image_urls = [
    "images/angle_1693733578_0.png",
    "images/angle_1693733578_1.png",
    "images/angle_1693733578_2.png",
]

# Initialize the current images
current_images = random.sample(image_urls, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_image = request.form['selected_image']
        if selected_image in current_images:
            current_images.remove(selected_image)
            current_images.append(random.choice(image_urls))
    return render_template('index.html', image1=current_images[0], image2=current_images[1])

if __name__ == '__main__':
    app.run(debug=True)