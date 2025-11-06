# Lottie Animations

This directory contains Lottie animation JSON files for gamification features.

## Where to Download Animations

Visit **LottieFiles.com** to download free, professional animations:
https://lottiefiles.com/featured

## Required Animations for Our Project

### 1. Flame Animation (BADGE_FLAME_GOLD.json)
- **Rename to**: `flame.json`
- **Use**: 
  - Daily streak widget (animated fire icon)
  - 7-day streak celebration
- **Status**: ⏳ **UPLOAD NEEDED**

### 2. Fist Animation (BADGE_FIST_GOLD.json)
- **Rename to**: `fist.json`
- **Use**: 
  - 14-day streak celebration
  - Daily goal achievement
- **Status**: ⏳ **UPLOAD NEEDED**

### 3. Arm Animation (BADGE_ARM_GOLD.json)
- **Rename to**: `arm.json`
- **Use**: 
  - 30-day streak celebration
  - Category completion
- **Status**: ⏳ **UPLOAD NEEDED**

## Optional Animations (Future)

### 4. Progress Bar
- **Use**: Loading states
- **Search**: "loading progress bar"
- **Save as**: `progress-bar.json`

### 5. Confetti Celebration
- **Use**: Major achievements (exam pass, 100 questions)
- **Search**: "confetti celebration"
- **Save as**: `confetti.json`

## How to Download

1. Go to LottieFiles.com
2. Search for the animation
3. Click "Download" → "Lottie JSON"
4. Save the JSON file to this directory
5. Update the animation URLs in the template to use local files:
   ```html
   src="/static/animations/fire.json"
   ```

## Current Status

✅ Lottie Player library added to template
✅ Celebration overlay implemented
✅ Streak widget with animation support
⏳ Animation JSON files need to be downloaded

## Alternative: Use CDN URLs

If you prefer not to download files, you can use CDN URLs:
- Fire: `https://lottie.host/4d7e3e0a-3f6c-4c7d-8e9f-1a2b3c4d5e6f/fire.json`
- Trophy: `https://lottie.host/embed/trophy-gold.json`
- Success: `https://lottie.host/embed/success-check.json`

**Note**: CDN URLs require internet connection and may be slower than local files.

