"""
Visual Regression Testing Service
Advanced screenshot comparison with multiple algorithms
"""

from PIL import Image, ImageChops, ImageDraw, ImageFilter
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from typing import Dict, List, Tuple, Optional
import hashlib
import os
from pathlib import Path
from datetime import datetime
import json


class VisualTestingService:
    """Service for visual regression testing"""
    
    def __init__(self, storage_path: str = "uploads/visual_tests"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.storage_path / "baselines").mkdir(exist_ok=True)
        (self.storage_path / "screenshots").mkdir(exist_ok=True)
        (self.storage_path / "diffs").mkdir(exist_ok=True)
    
    def compare_images(
        self,
        baseline_path: str,
        screenshot_path: str,
        threshold: float = 0.1,
        ignore_regions: List[Dict] = None
    ) -> Dict:
        """
        Compare two images using multiple algorithms
        
        Args:
            baseline_path: Path to baseline image
            screenshot_path: Path to current screenshot
            threshold: Acceptable difference threshold (0-1)
            ignore_regions: List of regions to ignore [{x, y, width, height}]
            
        Returns:
            Dictionary with comparison results
        """
        # Load images
        baseline = Image.open(baseline_path).convert('RGB')
        screenshot = Image.open(screenshot_path).convert('RGB')
        
        # Ensure same size
        if baseline.size != screenshot.size:
            # Resize screenshot to match baseline
            screenshot = screenshot.resize(baseline.size, Image.Resampling.LANCZOS)
        
        # Apply ignore regions if specified
        if ignore_regions:
            baseline = self._mask_regions(baseline, ignore_regions)
            screenshot = self._mask_regions(screenshot, ignore_regions)
        
        # Perform multiple comparison methods
        results = {}
        
        # 1. Pixel-by-pixel comparison
        results['pixel_diff'] = self._pixel_difference(baseline, screenshot)
        
        # 2. Structural Similarity Index (SSIM)
        results['ssim'] = self._calculate_ssim(baseline, screenshot)
        
        # 3. Mean Squared Error (MSE)
        results['mse'] = self._calculate_mse(baseline, screenshot)
        
        # 4. Histogram comparison
        results['histogram_similarity'] = self._histogram_comparison(baseline, screenshot)
        
        # 5. Perceptual hash difference
        results['hash_distance'] = self._perceptual_hash_distance(baseline, screenshot)
        
        # Generate diff image
        diff_image, highlighted_diff = self._generate_diff_image(baseline, screenshot)
        
        # Calculate overall metrics
        difference_percentage = results['pixel_diff']['different_pixels_percentage']
        passed = difference_percentage <= (threshold * 100)
        
        return {
            'passed': passed,
            'difference_percentage': difference_percentage,
            'pixel_difference_count': results['pixel_diff']['different_pixels'],
            'total_pixels': results['pixel_diff']['total_pixels'],
            'ssim_score': results['ssim'],
            'mse_score': results['mse'],
            'histogram_similarity': results['histogram_similarity'],
            'hash_distance': results['hash_distance'],
            'threshold': threshold * 100,
            'diff_image': diff_image,
            'highlighted_diff': highlighted_diff,
            'dimensions': {
                'width': baseline.size[0],
                'height': baseline.size[1]
            }
        }
    
    def _pixel_difference(self, img1: Image.Image, img2: Image.Image) -> Dict:
        """Calculate pixel-by-pixel difference"""
        # Convert to numpy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Calculate absolute difference
        diff = np.abs(arr1.astype(int) - arr2.astype(int))
        
        # Count different pixels (any channel difference > 0)
        different_pixels = np.sum(np.any(diff > 0, axis=2))
        total_pixels = arr1.shape[0] * arr1.shape[1]
        
        return {
            'different_pixels': int(different_pixels),
            'total_pixels': int(total_pixels),
            'different_pixels_percentage': (different_pixels / total_pixels) * 100
        }
    
    def _calculate_ssim(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Calculate Structural Similarity Index
        Returns value between -1 and 1 (1 = identical)
        """
        # Convert to grayscale numpy arrays
        gray1 = np.array(img1.convert('L'))
        gray2 = np.array(img2.convert('L'))
        
        # Calculate SSIM
        score, _ = ssim(gray1, gray2, full=True)
        return float(score)
    
    def _calculate_mse(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate Mean Squared Error"""
        arr1 = np.array(img1).astype(float)
        arr2 = np.array(img2).astype(float)
        
        mse = np.mean((arr1 - arr2) ** 2)
        return float(mse)
    
    def _histogram_comparison(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Compare histograms of images
        Returns similarity score 0-1 (1 = identical)
        """
        # Get histograms for each channel
        hist1_r = img1.split()[0].histogram()
        hist1_g = img1.split()[1].histogram()
        hist1_b = img1.split()[2].histogram()
        
        hist2_r = img2.split()[0].histogram()
        hist2_g = img2.split()[1].histogram()
        hist2_b = img2.split()[2].histogram()
        
        # Calculate correlation for each channel
        corr_r = self._histogram_correlation(hist1_r, hist2_r)
        corr_g = self._histogram_correlation(hist1_g, hist2_g)
        corr_b = self._histogram_correlation(hist1_b, hist2_b)
        
        # Average correlation
        return (corr_r + corr_g + corr_b) / 3
    
    def _histogram_correlation(self, hist1: List, hist2: List) -> float:
        """Calculate correlation between two histograms"""
        # Convert to numpy arrays
        h1 = np.array(hist1, dtype=float)
        h2 = np.array(hist2, dtype=float)
        
        # Normalize
        h1 = h1 / np.sum(h1)
        h2 = h2 / np.sum(h2)
        
        # Calculate correlation
        corr = np.corrcoef(h1, h2)[0, 1]
        return float(corr) if not np.isnan(corr) else 0.0
    
    def _perceptual_hash_distance(self, img1: Image.Image, img2: Image.Image) -> int:
        """
        Calculate perceptual hash distance (dHash)
        Returns hamming distance (0 = identical)
        """
        hash1 = self._dhash(img1)
        hash2 = self._dhash(img2)
        
        # Calculate hamming distance
        return bin(hash1 ^ hash2).count('1')
    
    def _dhash(self, image: Image.Image, hash_size: int = 8) -> int:
        """Generate difference hash"""
        # Resize and convert to grayscale
        resized = image.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS).convert('L')
        
        # Calculate horizontal gradient
        pixels = list(resized.getdata())
        difference = []
        
        for row in range(hash_size):
            for col in range(hash_size):
                pixel_left = pixels[row * (hash_size + 1) + col]
                pixel_right = pixels[row * (hash_size + 1) + col + 1]
                difference.append(pixel_left > pixel_right)
        
        # Convert to integer
        hash_value = 0
        for bit in difference:
            hash_value = (hash_value << 1) | bit
        
        return hash_value
    
    def _generate_diff_image(
        self,
        img1: Image.Image,
        img2: Image.Image
    ) -> Tuple[Image.Image, Image.Image]:
        """
        Generate difference visualization images
        
        Returns:
            (basic_diff, highlighted_diff)
        """
        # Basic diff using ImageChops
        basic_diff = ImageChops.difference(img1, img2)
        
        # Create highlighted diff
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Calculate absolute difference
        diff = np.abs(arr1.astype(int) - arr2.astype(int))
        
        # Create mask of different pixels
        mask = np.any(diff > 10, axis=2)  # Threshold to ignore minor differences
        
        # Create highlighted image (red overlay on differences)
        highlighted = arr2.copy()
        highlighted[mask] = [255, 0, 0]  # Red
        
        # Blend with original for semi-transparent effect
        alpha = 0.5
        highlighted = (alpha * highlighted + (1 - alpha) * arr2).astype(np.uint8)
        
        highlighted_img = Image.fromarray(highlighted)
        
        return basic_diff, highlighted_img
    
    def _mask_regions(self, image: Image.Image, regions: List[Dict]) -> Image.Image:
        """Mask (black out) specified regions"""
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        for region in regions:
            x = region['x']
            y = region['y']
            width = region['width']
            height = region['height']
            
            # Draw black rectangle
            draw.rectangle([x, y, x + width, y + height], fill='black')
        
        return img_copy
    
    def save_screenshot(
        self,
        image: Image.Image,
        test_id: int,
        screenshot_type: str = "screenshot"
    ) -> str:
        """
        Save screenshot to storage
        
        Args:
            image: PIL Image object
            test_id: Visual test ID
            screenshot_type: baseline, screenshot, or diff
            
        Returns:
            Relative path to saved image
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{test_id}_{screenshot_type}_{timestamp}.png"
        
        if screenshot_type == "baseline":
            folder = self.storage_path / "baselines"
        elif screenshot_type == "diff":
            folder = self.storage_path / "diffs"
        else:
            folder = self.storage_path / "screenshots"
        
        filepath = folder / filename
        image.save(filepath, 'PNG', optimize=True)
        
        # Return relative path
        return str(filepath.relative_to(self.storage_path.parent))
    
    def calculate_image_hash(self, image_path: str) -> str:
        """Calculate MD5 hash of image file"""
        hasher = hashlib.md5()
        with open(image_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    
    def get_image_info(self, image_path: str) -> Dict:
        """Get image metadata"""
        img = Image.open(image_path)
        file_size = os.path.getsize(image_path)
        
        return {
            'width': img.size[0],
            'height': img.size[1],
            'format': img.format,
            'mode': img.mode,
            'file_size': file_size,
            'hash': self.calculate_image_hash(image_path)
        }
    
    def create_thumbnail(
        self,
        image_path: str,
        max_size: Tuple[int, int] = (400, 300)
    ) -> str:
        """Create thumbnail for preview"""
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        thumb_path = image_path.replace('.png', '_thumb.png')
        img.save(thumb_path, 'PNG')
        
        return thumb_path
    
    def apply_anti_aliasing_tolerance(
        self,
        img1: Image.Image,
        img2: Image.Image,
        tolerance: int = 2
    ) -> bool:
        """
        Check if differences are within anti-aliasing tolerance
        Useful for ignoring minor rendering differences
        """
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        diff = np.abs(arr1.astype(int) - arr2.astype(int))
        significant_diff = np.any(diff > tolerance, axis=2)
        
        return np.sum(significant_diff) == 0
