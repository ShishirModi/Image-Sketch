import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageChops
from io import BytesIO
import numpy as np
import cv2

st.set_page_config(page_title="Artistic Image Converter", page_icon="🎨", layout="wide")

def wcsketch(input_img, sigma_s=50, sigma_r=0.5):
    img_1 = cv2.edgePreservingFilter(input_img, flags=2, sigma_s=sigma_s, sigma_r=sigma_r)
    img_water_color = cv2.stylization(img_1, sigma_s=100, sigma_r=0.5)
    return img_water_color

def pencilsketch(input_img, shade_factor=0.5):
    img_gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (21, 21), 0)
    img_blend = cv2.divide(img_gray, img_blur, scale=256.0)
    img_pencil_shade = cv2.filter2D(img_blend, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
    
    img_pencil_shade = cv2.cvtColor(img_pencil_shade, cv2.COLOR_GRAY2BGR)
    img_pencil_shade = cv2.bitwise_not(img_pencil_shade)
    
    img_pencil_shade = cv2.cvtColor(img_pencil_shade, cv2.COLOR_BGR2GRAY)
    img_pencil_shade = cv2.bitwise_not(img_pencil_shade)
    img_pencil_shade = cv2.cvtColor(img_pencil_shade, cv2.COLOR_GRAY2BGR)
    
    height, width, _ = img_pencil_shade.shape
    for _ in range(height * width // 100):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        color = np.random.randint(0, 256, size=3)
        img_pencil_shade[y, x] = color
    return img_pencil_shade

def modern_art(input_img, emboss_strength=2, edge_strength=1, color1='#FF0000', color2='#00FF00'):
    img_pil = Image.fromarray(input_img)
    img_modern = img_pil.filter(ImageFilter.EMBOSS)
    img_modern = img_modern.filter(ImageFilter.FIND_EDGES)
    img_modern = img_modern.filter(ImageFilter.EDGE_ENHANCE)
    img_modern = ImageOps.colorize(img_modern.convert('L'), color1, color2)
    return np.array(img_modern)

def gothic(input_img, brightness_factor=0.5, contrast_factor=1.5, glow_strength=10, creepiness_level=30):
    img_pil = Image.fromarray(input_img)
    enhancer = ImageEnhance.Brightness(img_pil)
    img_dark = enhancer.enhance(brightness_factor)
    
    enhancer = ImageEnhance.Contrast(img_dark)
    img_gothic = enhancer.enhance(contrast_factor)
    
    img_gothic = img_gothic.convert('RGB')
    r, g, b = img_gothic.split()
    g = ImageChops.multiply(g, ImageEnhance.Brightness(g).enhance(1.2))
    img_gothic = Image.merge('RGB', (r, g, b))
    
    img_glow = img_gothic.filter(ImageFilter.GaussianBlur(radius=glow_strength))
    img_gothic = Image.blend(img_gothic, img_glow, alpha=0.3)
    
    np_img = np.array(img_gothic)
    noise = np.random.normal(scale=creepiness_level, size=np_img.shape)
    noisy_img = np_img + noise
    noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
    
    return noisy_img

def load_image(image):
    try:
        img = Image.open(image)
        img = img.convert("RGB")
        return img
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def compress_image(image, quality=50):
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()

def display_image(image, title, download_label, file_name):
    st.header(title)
    st.image(image, use_column_width=True)
    byte_img = compress_image(image)
    st.download_button(label=download_label, data=byte_img, file_name=file_name, mime="image/jpeg")

def main():
    st.title('🎨 image 👉 sketch')
    st.markdown("""
        **Convert your images into various artistic effects:**
        - **Water Color Sketch**
        - **Pencil Sketch**
        - **Gothic**
        - **Modern Art**
    """)
    
    st.sidebar.header("Upload Image")
    image_file = st.sidebar.file_uploader("Upload Images", type=["png", "jpg", "jpeg"])

    if image_file is not None:
        image = load_image(image_file)
        if image is not None:
            st.sidebar.header("Select Conversion Type")
            option = st.sidebar.selectbox('Choose an effect', 
                                          ('Water Color Sketch', 'Pencil Sketch', 'Gothic', 'Modern Art'))

            col1, col2 = st.columns([1, 2])
            with col1:
                st.header("Original Image")
                st.image(image, use_column_width=True)

            compressed_image = Image.open(BytesIO(compress_image(image, quality=50)))

            with col2:
                if option == 'Water Color Sketch':
                    sigma_s = st.slider("Sigma S", min_value=1, max_value=100, value=50, step=1)
                    sigma_r = st.slider("Sigma R", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
                    with st.spinner("Converting to Water Color Sketch..."):
                        final_sketch = wcsketch(np.array(compressed_image), sigma_s=sigma_s, sigma_r=sigma_r)
                    if final_sketch is not None:
                        im_pil = Image.fromarray(final_sketch)
                        display_image(im_pil, "Water Color Sketch", "Download Water Color Sketch", "watercolorsketch.jpg")

                elif option == 'Pencil Sketch':
                    shade_factor = st.slider("Shade Factor", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
                    with st.spinner("Converting to Pencil Sketch..."):
                        final_sketch = pencilsketch(np.array(compressed_image), shade_factor=shade_factor)
                    if final_sketch is not None:
                        im_pil = Image.fromarray(final_sketch)
                        display_image(im_pil, "Pencil Sketch", "Download Pencil Sketch", "pencilsketch.jpg")

                elif option == 'Gothic':
                    brightness_factor = st.slider("Brightness Factor", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
                    contrast_factor = st.slider("Contrast Factor", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
                    glow_strength = st.slider("Glow Strength", min_value=0, max_value=20, value=10, step=1)
                    creepiness_level = st.slider("Creepiness Level", min_value=0, max_value=100, value=30, step=1)
                    with st.spinner("Converting to Gothic Effect..."):
                        final_gothic = gothic(np.array(compressed_image), brightness_factor=brightness_factor, contrast_factor=contrast_factor, glow_strength=glow_strength, creepiness_level=creepiness_level)
                    if final_gothic is not None:
                        im_pil = Image.fromarray(final_gothic)
                        display_image(im_pil, "Gothic Effect", "Download Gothic Effect", "gothic.jpg")

                elif option == 'Modern Art':
                    emboss_strength = st.slider("Emboss Strength", min_value=1, max_value=5, value=2, step=1)
                    edge_strength = st.slider("Edge Strength", min_value=1, max_value=5, value=1, step=1)
                    color1 = st.color_picker("Color 1", "#FF0000")
                    color2 = st.color_picker("Color 2", "#00FF00")
                    with st.spinner("Converting to Modern Art Effect..."):
                        final_modern_art = modern_art(np.array(compressed_image), emboss_strength=emboss_strength, edge_strength=edge_strength, color1=color1, color2=color2)
                    if final_modern_art is not None:
                        im_pil = Image.fromarray(final_modern_art)
                        display_image(im_pil, "Modern Art Effect", "Download Modern Art Effect", "modernart.jpg")

    else:
        st.image("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJ4AAACUCAMAAABVwGAvAAAAY1BMVEX///8AAAC0tLTs7Oz19fVLS0t1dXWtra04ODggICDg4OAxMTGAgIDw8PDb29v6+vpcXFyenp6VlZVvb2/U1NS7u7srKytmZmZWVlanp6eLi4tFRUXm5uYSEhLLy8s9PT0ZGRkqJZzeAAAEXElEQVR4nO2c2ZaDIAyGy6i1m7vVLtr2/Z9yugoqKESCnTP8l2MZvhMhhBBcLKysrCQV7pdbgqh1dswjKFy1KzDZ3oTlBQTnpvhsL5WVOp1TmqIjZBUq2+5qju7+hnNFutgk3V2OEp6xcfdRpjKBN6bpCDkq4GXm8dbydDnr77Yemq41089eGu/IwPkApySrYH+gPcWyraJl06ZGhHsooHyrQLYNXWflLQ6UQwef7OJGm3jIxrurVDYFxVuikj1Fx/mPZAujeL7Fm6B/jOeGeZ5X4HAcFy/fxUVd365Z6n4fXsiEhDUcEAlvT1qKoQ4cB+9IOio2X4S379Ld10zZJR0fr1r18cjua/B2HDpCQPtpBLyKSycfUCLjJXw8AvEuCHgHHhuBBa/68SJR1ur0FXiuKHEFiSAM4mVfgReJ8CCeD2FqnAV4KokIRDy+VyYEsuwi4IV8uhuADgPP9bS9W5Q198KjO4BCFpSAijf6YBl2nHC0v66BXi0WXtDNUPowOqy9RtRKPxeKqXV0vHvUd3pP4Fvsw7e6iNtw5+InSbLPRVM29/1RTz1bEiN8GnfM3cyF99kuxcMnKjPhhU3c4A3yzYO3YSLqQb5Z8KrWqhwPjL858MLObmQr3sPNgFf14tVSaD/zeCHnLPgs4jOOV3FPqkX+xTTehh+riuaHYTxu8uopj8tnFs8RJTjuKnnz1yjeZrAq58rhM4nnCMZdY7/++9WLVyWnozDLLZoVVP34RSveK0RO+dGnI5wVVL35qxPv9P57ymtWSdW+dOeHRryd6MGTTsJ2D3ltPn147Oa2Z78hj9JW1uLThndqddJJlm1EWasx++nCO3U6adlvzKO0xfoXTXj9qiqGT25WMHzUfnrwOKdUNNMdKFfT0SS5HrwfXifJm069EpGOXES8lxH6sfG34D3s50AqEQ3hkbSS9ndz4BHJtWIuPJgsnh68xqHW6gVyBvCcj1s6yKYwjeI1hxDS6V+zeIvLua7rg3xy2jDeYpFfVDLnxvHUZPEsnsWzeH8fL3JVjgwN40X+slzKRlPG8dxXyCJ/WcgoXvQ5VpeuDzOKl3/+JF0ba4N5i2fx5PGKrUYVuhNowUar6PHkP77tokEWb4qm4EEKkRU1Be+Mf0dSHY+5Va8QJQKljsfcz5XPG0Gljsc0ISTN3Snq//P284jeifKjsaZvtSoC1qspijs5z+Tc+QGtvy+u7SeesBxVVHUOEdtJoHYGshNY0BlvKq0bM3y7p5pjEg3H3i25CWJ2ZapNeZUlD0UaP5wQN30IrgIMSFiYCDqLMofnLscby4nZwKo29cTeJfLr8fYSYr+1ovqhksFK9yAFnNR2VbOX11y1qcstl2FUXdK4WE/Rrr0qRvtD5wf0Fd3aD24l+iclJESLFPDDD4AAIYFJWbwpsnhTZPGmyOJNkcWbIos3RX8G7xvCu56am8jQD7oga7DQfX65r8JYA4lYoC7ZIVP+tKeVlSn9AkpnUNWlTtc1AAAAAElFTkSuQmCC", caption="Please upload an image to get started.")

    # Feedback button
    if st.sidebar.button('Feedback'):
        st.sidebar.write("We value your feedback! Please share your thoughts or issues:")
        feedback = st.text_area("Feedback", placeholder="Type your feedback here...")
        if st.button("Submit Feedback"):
            if feedback:
                # You can add functionality to send feedback via email or save to a file
                st.success("Thank you for your feedback!")
                # Example: Save feedback to a file (you could also send it via email)
                with open("feedback.txt", "a") as f:
                    f.write(feedback + "\n")
            else:
                st.warning("Please enter your feedback before submitting.")

if __name__ == '__main__':
    main()
