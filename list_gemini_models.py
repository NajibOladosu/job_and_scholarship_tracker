#!/usr/bin/env python
"""
List available Gemini models for the configured API key.
This helps us find the correct model name to use.
"""
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
import google.generativeai as genai

print("=" * 60)
print("GEMINI API - AVAILABLE MODELS")
print("=" * 60)

# Configure API
genai.configure(api_key=settings.GEMINI_API_KEY)

print("\nFetching available models...")
print("-" * 60)

try:
    # List all available models
    models = genai.list_models()

    print("\n✅ Available Models for Content Generation:\n")

    generation_models = []
    for model in models:
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            generation_models.append(model)
            print(f"📌 {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")
            print()

    if generation_models:
        print("=" * 60)
        print("RECOMMENDED MODEL NAMES TO USE:")
        print("=" * 60)
        for model in generation_models[:3]:  # Show top 3
            # Extract just the model name (remove 'models/' prefix if present)
            model_name = model.name.replace('models/', '')
            print(f"  - '{model_name}'")
            print(f"    or")
            print(f"  - '{model.name}'")
            print()
    else:
        print("⚠️  No models found that support generateContent!")
        print("   This might indicate an API key issue.")

except Exception as e:
    print(f"\n❌ Error listing models: {e}")
    print("\nThis could be due to:")
    print("  1. Invalid or expired API key")
    print("  2. API quota exceeded")
    print("  3. Network connectivity issues")
    print("  4. API version mismatch")

print("\n" + "=" * 60)
