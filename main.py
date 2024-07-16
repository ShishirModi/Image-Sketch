import streamlit as st 
from PIL import Image 
from io import BytesIO 
import numpy as np 
import cv2

def wcsketch(input_img): 
	img_1 = cv2.edgePreservingFilter(input_img, flags=2, sigma_s=50, sigma_r=0.8) 
	img_water_color = cv2.stylization(img_1, sigma_s=100, sigma_r=0.5) 
	return(img_water_color) 

def pencilsketch(input_img): 

	img_gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
	img_inverted = cv2.bitwise_not(img_gray)
	img_blur = cv2.GaussianBlur(img_inverted, (21, 21), 0)
	img_blend = cv2.divide(img_gray, img_blur, scale=256.0)

	# Apply pencil shade effect
	kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
	img_pencil_shade = cv2.filter2D(img_blend, -1, kernel)
	img_pencil_shade = cv2.cvtColor(img_pencil_shade, cv2.COLOR_GRAY2BGR)

	# Add randomness to simulate hand-drawn effect
	height, width, _ = img_pencil_shade.shape
	for _ in range(height * width // 100):  # Adjust the percentage of randomness here
		x = np.random.randint(0, width)
		y = np.random.randint(0, height)
		color = np.random.randint(0, 256, size=3)
		img_pencil_shade[y, x] = color

	return img_pencil_shade

def loadimage(image): 
	img = Image.open(image) 
	return img 

def tune_parameters():
	sigma_s = st.slider("Sigma S", min_value=1, max_value=100, value=50, step=1)
	sigma_r = st.slider("Sigma R", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
	shade_factor = st.slider("Shade Factor", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
	return sigma_s, sigma_r, shade_factor

def main(): 
	
	st.title('Image ➡ Sketch') 
	st.write('''This is an application developed for converting your image to a ***Water Color Sketch*** or ***Pencil Sketch***''') 
	st.subheader("Upload your image") 
	
	image_file = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"]) 

	if image_file is not None: 
		
		option = st.selectbox('How would you like to convert the image', 
							('Water Color Sketch', 
							'Pencil Sketch')) 
		if option == 'Water Color Sketch': 
			image = Image.open(image_file) 
			final_sketch = wcsketch(np.array(image)) 
			im_pil = Image.fromarray(final_sketch) 

			col1, col2 = st.columns(2) 
			with col1: 
				st.header("Original Image") 
				st.image(loadimage(image_file), width=250) 

			with col2: 
				st.header("Water Color Sketch") 
				st.image(im_pil, width=250) 
				buf = BytesIO() 
				img = im_pil 
				img.save(buf, format="JPEG") 
				byte_im = buf.getvalue() 
				st.download_button( 
					label="Download Sketch", 
					data=byte_im, 
					file_name="watercolorsketch.png", 
					mime="image/png"
				) 

			sigma_s, sigma_r, shade_factor = tune_parameters()
			img_1 = cv2.edgePreservingFilter(np.array(image), flags=2, sigma_s=sigma_s, sigma_r=sigma_r) 
			img_water_color = cv2.stylization(img_1, sigma_s=100, sigma_r=shade_factor) 
			im_pil = Image.fromarray(img_water_color) 

			st.header("Tuned Water Color Sketch") 
			st.image(im_pil, width=250) 
			buf = BytesIO() 
			img = im_pil 
			img.save(buf, format="JPEG") 
			byte_im = buf.getvalue() 
			st.download_button( 
				label="Download Sketch", 
				data=byte_im, 
				file_name="tunedwatercolorsketch.png", 
				mime="image/png"
			) 

		if option == 'Pencil Sketch': 
			image = Image.open(image_file) 
			final_sketch = pencilsketch(np.array(image)) 
			im_pil = Image.fromarray(final_sketch) 

			col1, col2 = st.columns(2) 
			with col1: 
				st.header("Original Image") 
				st.image(loadimage(image_file), width=250) 

			with col2: 
				st.header("Pencil Sketch") 
				st.image(im_pil, width=250) 
				buf = BytesIO() 
				img = im_pil 
				img.save(buf, format="JPEG") 
				byte_im = buf.getvalue() 
				st.download_button( 
					label="Download Sketch", 
					data=byte_im, 
					file_name="pencilsketch.png", 
					mime="image/png"
				) 

			sigma_s, sigma_r, shade_factor = tune_parameters()
			img_pencil_sketch, pencil_color_sketch = cv2.pencilSketch( 
				np.array(image), sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=shade_factor) 
			im_pil = Image.fromarray(img_pencil_sketch) 

			st.header("Tuned Pencil Sketch") 
			st.image(im_pil, width=250) 
			buf = BytesIO() 
			img = im_pil 
			img.save(buf, format="JPEG") 
			byte_im = buf.getvalue() 
			st.download_button( 
				label="Download Sketch", 
				data=byte_im, 
				file_name="tunedpencilsketch.png", 
				mime="image/png"
			) 

if __name__ == '__main__': 
	main() 
