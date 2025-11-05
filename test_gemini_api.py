#!/usr/bin/env python
"""
Test Gemini API connection and try different model names.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
import google.generativeai as genai

print("=" * 60)
print("GEMINI API CONNECTION TEST")
print("=" * 60)

# Configure API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Test different model names
model_names_to_try = [
    'gemini-pro',
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro-latest',
    'models/gemini-pro',
    'models/gemini-1.5-flash',
    'models/gemini-1.5-pro',
]

print("\nTrying different model names...\n")

successful_models = []

for model_name in model_names_to_try:
    try:
        print(f"Testing: {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)

        # Try a simple generation
        response = model.generate_content("Say 'test successful'")

        if response and response.text:
            print(f"✅ SUCCESS")
            print(f"   Response: {response.text[:50]}")
            successful_models.append(model_name)
        else:
            print(f"⚠️  No response")

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"❌ Not found (404)")
        elif "403" in error_msg:
            print(f"❌ Forbidden (403) - Check API key")
        elif "429" in error_msg:
            print(f"❌ Rate limit exceeded")
        else:
            print(f"❌ Error: {error_msg[:50]}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if successful_models:
    print(f"\n✅ Working models found: {len(successful_models)}")
    for model in successful_models:
        print(f"   - {model}")
    print(f"\n💡 Use this in gemini_service.py:")
    print(f"   self.model = genai.GenerativeModel('{successful_models[0]}')")
else:
    print("\n❌ No working models found!")
    print("\nPossible issues:")
    print("  1. Invalid GEMINI_API_KEY")
    print("  2. API key doesn't have access to Gemini models")
    print("  3. Quota exceeded")
    print("  4. Library version incompatibility")
    print(f"\nCurrent library: google-generativeai")
    print(f"Consider upgrading to latest version")

print("\n" + "=" * 60)
