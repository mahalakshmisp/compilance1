# Android APK Packaging Instructions

This repository contains a Flask web application. To create an Android APK, use one of the following approaches:

## Option 1: Use BeeWare Briefcase (recommended for a Python-based APK)

1. Install Briefcase:

```bash
python -m pip install briefcase
```

2. Create a new Android app skeleton from the repo root:

```bash
briefcase new
```

3. Configure the generated `pyproject.toml` to include `Flask` and `google-generativeai`.

4. Build the Android app:

```bash
briefcase build android
briefcase package android
```

5. Install the APK on your device:

```bash
briefcase run android
```

> Notes:
> - Android packaging requires the Android SDK, NDK, and Java JDK.
> - The current repo is a Flask app, so the APK will need to launch a local web server and display a web view.

## Option 2: Use Termux / Pydroid for local execution

If you only need to run the app on Android without creating a distributable APK, use Termux or Pydroid:

- Install Python and Flask in Termux or Pydroid
- Copy the repository files onto the Android device
- Run `python app.py`
- Open `http://127.0.0.1:5000` in the Android browser

## Recommended model configuration for Android

Set these environment variables before running the app:

```bash
export GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY'
export GOOGLE_MODEL='models/gemini-flash-latest'
```

## Important

A true APK build from this Flask app requires additional Android-specific packaging and a webview wrapper. The files in this repository provide the Flask backend and Windows `.exe` packaging support.
