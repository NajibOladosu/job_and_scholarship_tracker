#!/usr/bin/env python
"""
Quick script to verify document processing and extraction.
Run: python verify_extraction.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from documents.models import Document, ExtractedInformation

User = get_user_model()

def verify_extraction():
    """Verify document processing and extraction."""
    print("=" * 60)
    print("DOCUMENT PROCESSING VERIFICATION")
    print("=" * 60)

    # Get first user (or modify to get specific user)
    users = User.objects.all()
    if not users.exists():
        print("❌ No users found in database")
        return

    for user in users:
        print(f"\n👤 User: {user.email}")
        print("-" * 60)

        # Check documents
        docs = Document.objects.filter(user=user)
        print(f"\n📄 Total Documents: {docs.count()}")

        if docs.exists():
            for doc in docs:
                status = "✅ Processed" if doc.is_processed else "⏳ Pending"
                print(f"  - {doc.original_filename}")
                print(f"    Type: {doc.get_document_type_display()}")
                print(f"    Status: {status}")
                print(f"    Size: {doc.file_size_mb} MB")
                if doc.processed_at:
                    print(f"    Processed: {doc.processed_at}")

        # Check extracted information
        extracted = ExtractedInformation.objects.filter(document__user=user)
        print(f"\n📊 Extracted Information: {extracted.count()} records")

        if extracted.exists():
            for info in extracted:
                print(f"\n  📌 {info.get_data_type_display()}")
                print(f"     Document: {info.document.original_filename}")
                print(f"     Confidence: {info.confidence_percentage}%")
                print(f"     Content Preview:")

                # Pretty print content based on type
                content = info.content
                if isinstance(content, list):
                    if len(content) > 0:
                        for i, item in enumerate(content[:3], 1):  # Show first 3 items
                            if isinstance(item, dict):
                                print(f"       {i}. {item}")
                            else:
                                print(f"       {i}. {item}")
                        if len(content) > 3:
                            print(f"       ... and {len(content) - 3} more")
                    else:
                        print(f"       (empty list)")
                elif isinstance(content, dict):
                    for key, value in list(content.items())[:5]:  # Show first 5 keys
                        print(f"       {key}: {value}")
                else:
                    preview = str(content)[:100]
                    print(f"       {preview}...")
        else:
            print("\n  ⚠️  No extracted information found!")
            print("     This means the document was uploaded but extraction failed.")
            print("     Check Celery worker logs for errors.")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    verify_extraction()
