from __future__ import annotations

from datetime import date


def create_complaint(
    *,
    name: str,
    description: str,
    category: str,
    location: str = "",
    authority: str = "",
) -> str:
    recipient = authority or "The Appropriate Authority"
    location_line = location or "[City/Region]"

    return f"""Date: {date.today().strftime("%d %B %Y")}

To:
{recipient}
{location_line}

Subject: Complaint concerning a possible {category.lower()} violation

Dear Sir/Madam,

I, {name}, respectfully submit this complaint regarding a matter that may involve a violation of human rights.

Description of the matter:

{description}

I request that the appropriate authority:

1. Acknowledge and register this complaint.
2. Conduct a fair, prompt, and impartial review.
3. Preserve and examine relevant records and evidence.
4. Protect the complainant and witnesses from retaliation.
5. Provide information about available remedies and next steps.
6. Communicate the outcome in writing.

I am prepared to provide supporting documents, messages, photographs, medical records, witness information, or other relevant evidence where available.

I request that my personal information be handled confidentially to the extent permitted by law.

Yours faithfully,

{name}
Contact information: [Add phone number or email]
Signature: ______________________
"""
