# 📦 How to Add Your Lottie Animation Files

## Files You Need to Upload

You have 3 Lottie animation files that need to be added to this directory:

### 1. BADGE_FLAME_GOLD.json
- **Rename to**: `flame.json`
- **Used for**: 
  - Streak widget (animated fire icon)
  - 7-day streak celebration
- **Location**: `/static/animations/flame.json`

### 2. BADGE_FIST_GOLD.json
- **Rename to**: `fist.json`
- **Used for**:
  - 14-day streak celebration
  - Daily goal achievement
- **Location**: `/static/animations/fist.json`

### 3. BADGE_ARM_GOLD.json
- **Rename to**: `arm.json`
- **Used for**:
  - 30-day streak celebration
  - Category completion
- **Location**: `/static/animations/arm.json`

## How to Upload (Step by Step)

### Option 1: Using Finder (macOS)
1. Open Finder
2. Navigate to: `/Users/evgenijbutov/Desktop/demo/flask-app 2/dental-academy-clean/static/animations/`
3. Copy your 3 files here
4. Rename them:
   - `BADGE_FLAME_GOLD.json` → `flame.json`
   - `BADGE_FIST_GOLD.json` → `fist.json`
   - `BADGE_ARM_GOLD.json` → `arm.json`

### Option 2: Using Terminal
```bash
# Navigate to animations directory
cd "/Users/evgenijbutov/Desktop/demo/flask-app 2/dental-academy-clean/static/animations/"

# Copy and rename files (adjust source path as needed)
cp ~/Downloads/BADGE_FLAME_GOLD.json ./flame.json
cp ~/Downloads/BADGE_FIST_GOLD.json ./fist.json
cp ~/Downloads/BADGE_ARM_GOLD.json ./arm.json

# Verify files are there
ls -lh *.json
```

### Option 3: Using VS Code / Cursor
1. Open the project in your editor
2. Navigate to `static/animations/` folder
3. Drag and drop your 3 files into this folder
4. Right-click each file → Rename:
   - `BADGE_FLAME_GOLD.json` → `flame.json`
   - `BADGE_FIST_GOLD.json` → `fist.json`
   - `BADGE_ARM_GOLD.json` → `arm.json`

## Verify Files Are Correct

After uploading, run this command to verify:
```bash
ls -lh static/animations/*.json
```

You should see:
```
-rw-r--r--  flame.json
-rw-r--r--  fist.json
-rw-r--r--  arm.json
-rw-r--r--  fire.json (old placeholder - can be deleted)
-rw-r--r--  success-check.json (old placeholder - can be deleted)
-rw-r--r--  trophy-gold.json (old placeholder - can be deleted)
```

## Test Animations

After uploading files:

1. **Restart Flask server** (if running):
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   python3 run_local.py
   ```

2. **Open browser**: http://127.0.0.1:5002

3. **Go to Individual Plan tab**

4. **Test animations** using the buttons:
   - 🔥 7 Days → Shows `flame.json`
   - 💪 14 Days → Shows `fist.json`
   - 🏆 30 Days → Shows `arm.json`
   - 🎯 Goal Met → Shows `fist.json`
   - ✅ Category → Shows `arm.json`

## What's Already Integrated

✅ **Code is ready** - All references updated to use new files
✅ **Streak widget** - Will use `flame.json` when streak > 0
✅ **Celebrations** - Different animations for different achievements
✅ **Test buttons** - Easy testing interface added
✅ **Fallbacks** - Old animations will be used if new files not found

## Current Status

- [ ] `flame.json` - **MISSING** (upload needed)
- [ ] `fist.json` - **MISSING** (upload needed)
- [ ] `arm.json` - **MISSING** (upload needed)
- [x] `fire.json` - Old placeholder (can be deleted after upload)
- [x] `success-check.json` - Old placeholder (can be deleted after upload)
- [x] `trophy-gold.json` - Old placeholder (can be deleted after upload)

## After Upload

Once you upload the 3 new files, you can optionally delete the old placeholders:
```bash
rm static/animations/fire.json
rm static/animations/success-check.json
rm static/animations/trophy-gold.json
```

But it's not necessary - they won't interfere with anything.

## Need Help?

If animations don't show after upload:
1. Check file names are exactly: `flame.json`, `fist.json`, `arm.json`
2. Check files are in: `/static/animations/`
3. Restart Flask server
4. Clear browser cache (Cmd+Shift+R on Mac)
5. Check browser console for errors (F12 → Console tab)





