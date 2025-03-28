import os
import cv2
import numpy as np
import argparse
from PIL import Image

def generate_albedo(image_path, output_path):
    """Generates albedo map (simple copy)."""
    img = cv2.imread(image_path)
    if img is None:
        return False
    cv2.imwrite(output_path, img)
    return True

def generate_normal(image_path, output_path):
    """Generates normal map using the specified algorithm."""
    try:
        img = Image.open(image_path).convert('L')  # Open and convert to grayscale
        img_array = np.array(img, dtype=np.float32)  # Convert to NumPy array
        
        # Sobel Operator (Simplified for demonstration)
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        dx = convolve(img_array, sobel_x)
        dy = convolve(img_array, sobel_y)
        
        # Calculate Normal Vectors
        normal_x = dx
        normal_y = dy
        normal_z = np.ones_like(img_array) * 255  # Assuming a Z-component
        
        # Normalize
        magnitude = np.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
        normal_x /= magnitude
        normal_y /= magnitude
        normal_z /= magnitude
        
        # Scale and Offset to 0-255 range
        normal_x = (normal_x + 1) * 127.5
        normal_y = (normal_y + 1) * 127.5
        normal_z = (normal_z + 1) * 127.5
        
        # Create RGB Image
        normal_map = np.stack([normal_x, normal_y, normal_z], axis=-1).astype(np.uint8)
        normal_image = Image.fromarray(normal_map)
        
        normal_image.save(output_path)
        return True

    except Exception as e:
        print(f"Error generating normal map: {e}")
        return False

def generate_roughness(image_path, output_path):
    """Generates roughness map using gaussian."""
    img = cv2.imread(image_path)
    if img is None:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    roughness = cv2.GaussianBlur(edges, (5, 5), 0)
    roughness = cv2.normalize(roughness, None, 0, 255, cv2.NORM_MINMAX)
    cv2.imwrite(output_path, roughness)
    return True

def generate_metallic(image_path, output_path):
    """Generates metallic map using HSV."""
    img = cv2.imread(image_path)
    if img is None:
        return False
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_metallic = np.array([0, 0, 100])
    upper_metallic = np.array([180, 50, 255])
    metallic_mask = cv2.inRange(hsv, lower_metallic, upper_metallic)
    metallic_mask = cv2.morphologyEx(metallic_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cv2.imwrite(output_path, metallic_mask)
    return True

def generate_pbr_textures(image_path, output_folder, albedo_type, normal_type, roughness_type, metallic_type):
    """Generates PBR textures based on specified types."""
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    os.makedirs(output_folder, exist_ok=True)

    if albedo_type == "copy":
        albedo_path = os.path.join(output_folder, f"{image_name}_albedo.png")
        if generate_albedo(image_path, albedo_path):
            print(f"Albedo map saved to {albedo_path}")
        else:
            print(f"Failed to generate albedo for {image_path}")

    if normal_type == "sobel":
        normal_path = os.path.join(output_folder, f"{image_name}_normal.png")
        if generate_normal(image_path, normal_path):
            print(f"Normal map saved to {normal_path}")
        else:
            print(f"Failed to generate normal for {image_path}")

    if roughness_type == "gaussian":
        roughness_path = os.path.join(output_folder, f"{image_name}_rough.png")
        if generate_roughness(image_path, roughness_path):
            print(f"Roughness map saved to {roughness_path}")
        else:
            print(f"Failed to generate roughness for {image_path}")

    if metallic_type == "hsv":
        metallic_path = os.path.join(output_folder, f"{image_name}_metallic.png")
        if generate_metallic(image_path, metallic_path):
            print(f"Metallic map saved to {metallic_path}")
        else:
            print(f"Failed to generate metallic for {image_path}")

def convolve(image, kernel):
    """Simple convolution function."""
    
    kernel_height, kernel_width = kernel.shape
    image_height, image_width = image.shape
    
    pad_height = kernel_height // 2
    pad_width = kernel_width // 2
    
    padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='edge')
    output = np.zeros_like(image)
    
    for i in range(image_height):
        for j in range(image_width):
            output[i, j] = np.sum(padded_image[i:i+kernel_height, j:j+kernel_width] * kernel)
            
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PBR textures from an image.")
    parser.add_argument("image_path", help="Path to the input image file.")
    parser.add_argument("-o", "--output_folder", help="Path to the output folder (optional).")
    parser.add_argument("--albedo", choices=["none", "copy"], default="copy", help="Albedo generation type.")
    parser.add_argument("--normal", choices=["none", "sobel"], default="sobel", help="Normal generation type.")
    parser.add_argument("--roughness", choices=["none", "gaussian"], default="gaussian", help="Roughness generation type.")
    parser.add_argument("--metallic", choices=["none", "hsv"], default="hsv", help="Metallic generation type.")
    args = parser.parse_args()

    generate_pbr_textures(args.image_path, args.output_folder or os.path.splitext(os.path.basename(args.image_path))[0] + "_textures",
                           args.albedo, args.normal, args.roughness, args.metallic)