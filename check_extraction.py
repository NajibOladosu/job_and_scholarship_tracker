"""
Quick extraction check - run via: python manage.py shell < check_extraction.py
"""
from django.contrib.auth import get_user_model
from documents.models import Document, ExtractedInformation

User = get_user_model()

print("\n" + "="*60)
print("DOCUMENT EXTRACTION CHECK")
print("="*60)

users = User.objects.all()
for user in users:
    print(f"\n👤 User: {user.email}")

    # Documents
    docs = Document.objects.filter(user=user)
    processed = docs.filter(is_processed=True).count()
    print(f"📄 Documents: {docs.count()} total, {processed} processed")

    for doc in docs:
        status = "✅" if doc.is_processed else "⏳"
        print(f"  {status} {doc.original_filename} ({doc.get_document_type_display()})")

    # Extracted info
    extracted = ExtractedInformation.objects.filter(document__user=user)
    print(f"\n📊 Extracted Info: {extracted.count()} records")

    if extracted.exists():
        for info in extracted:
            print(f"\n  📌 {info.get_data_type_display()}")
            print(f"     From: {info.document.original_filename}")
            content = info.content
            if isinstance(content, list):
                print(f"     Items: {len(content)}")
                if len(content) > 0:
                    print(f"     Preview: {content[0] if len(content) > 0 else 'empty'}")
            elif isinstance(content, dict):
                print(f"     Keys: {list(content.keys())}")
            else:
                print(f"     Value: {str(content)[:100]}")
    else:
        print("  ⚠️ No extraction data found - check worker logs!")

print("\n" + "="*60 + "\n")
