from __future__ import annotations

from typing import Any

CATEGORY_RULES = [
    {
        "category": "Labor and Employment Rights",
        "issue": "Possible workplace or employment-rights violation",
        "keywords": [
            "salary",
            "wage",
            "unpaid",
            "employer",
            "employee",
            "workplace",
            "dismissed",
            "fired",
            "termination",
            "overtime",
            "harassment at work",
            "forced labor",
            "forced labour",
        ],
        "guidance": (
            "Keep employment contracts, attendance records, salary slips, "
            "messages, and bank statements. Submit a written request to the "
            "employer and consider contacting the appropriate labor authority, "
            "trade union, legal-aid service, or employment lawyer."
        ),
    },
    {
        "category": "Discrimination and Equality",
        "issue": "Possible discrimination or unequal treatment",
        "keywords": [
            "discrimination",
            "race",
            "religion",
            "religious",
            "caste",
            "ethnicity",
            "gender",
            "sex",
            "disability",
            "disabled",
            "pregnant",
            "pregnancy",
            "lgbt",
            "sexual orientation",
            "nationality",
            "unequal treatment",
        ],
        "guidance": (
            "Record what happened, when it occurred, who was involved, and "
            "whether witnesses or written evidence exist. Consider using the "
            "institution's grievance procedure and contacting an equality body, "
            "human-rights commission, legal-aid service, or qualified lawyer."
        ),
    },
    {
        "category": "Gender-Based Violence and Harassment",
        "issue": "Possible gender-based violence, abuse, or harassment",
        "keywords": [
            "sexual harassment",
            "sexual assault",
            "rape",
            "domestic violence",
            "stalking",
            "abusive partner",
            "molestation",
            "dowry",
            "forced marriage",
        ],
        "guidance": (
            "Prioritize immediate safety. Preserve messages, photographs, "
            "medical records, and witness details where this can be done safely. "
            "Contact trusted support services, medical care, law enforcement, "
            "a protection service, or a lawyer as appropriate."
        ),
    },
    {
        "category": "Child Rights",
        "issue": "Possible violation of a child's rights",
        "keywords": [
            "child",
            "minor",
            "underage",
            "child labor",
            "child labour",
            "school refused",
            "child abuse",
            "orphan",
        ],
        "guidance": (
            "A child's safety and best interests should come first. Preserve "
            "relevant evidence without questioning or pressuring the child. "
            "Contact an appropriate child-protection authority, trusted school "
            "official, social worker, legal-aid service, or emergency service."
        ),
    },
    {
        "category": "Privacy and Digital Rights",
        "issue": "Possible privacy, surveillance, or digital-rights violation",
        "keywords": [
            "privacy",
            "personal data",
            "data leak",
            "hacked",
            "hack",
            "surveillance",
            "tracked",
            "tracking",
            "doxxed",
            "doxxing",
            "online harassment",
            "account stolen",
            "photos shared",
            "video shared",
        ],
        "guidance": (
            "Change compromised passwords, enable multi-factor authentication, "
            "save screenshots and URLs, and report harmful content through the "
            "platform. Consider contacting a data-protection authority, "
            "cybercrime unit, digital-rights organization, or qualified lawyer."
        ),
    },
    {
        "category": "Freedom of Expression and Assembly",
        "issue": "Possible restriction on expression, protest, or association",
        "keywords": [
            "freedom of speech",
            "censorship",
            "protest",
            "demonstration",
            "assembly",
            "journalist",
            "reporter",
            "publication banned",
            "union banned",
        ],
        "guidance": (
            "Document the restriction, any official order, the people involved, "
            "and available witnesses. Seek advice from a legal-aid organization, "
            "civil-liberties group, journalist-support organization, or lawyer."
        ),
    },
    {
        "category": "Housing and Property Rights",
        "issue": "Possible housing, eviction, or property-rights violation",
        "keywords": [
            "eviction",
            "evicted",
            "landlord",
            "tenant",
            "rent",
            "homeless",
            "house demolished",
            "property seized",
            "land taken",
        ],
        "guidance": (
            "Keep tenancy documents, ownership records, notices, receipts, "
            "photographs, and communications. Avoid ignoring formal notices. "
            "Contact a housing authority, tenant-support organization, "
            "legal-aid service, or property lawyer."
        ),
    },
    {
        "category": "Access to Health Care",
        "issue": "Possible denial of health care or medical discrimination",
        "keywords": [
            "hospital refused",
            "doctor refused",
            "denied treatment",
            "medical negligence",
            "health care",
            "healthcare",
            "medicine denied",
            "ambulance refused",
        ],
        "guidance": (
            "Request written records and reasons for the decision, and preserve "
            "medical documents and receipts. Urgent symptoms require immediate "
            "medical attention. Complaints may be directed to the institution, "
            "health regulator, patient-rights body, or qualified lawyer."
        ),
    },
    {
        "category": "Education Rights",
        "issue": "Possible denial of access to education",
        "keywords": [
            "school admission",
            "college admission",
            "education denied",
            "expelled",
            "teacher harassment",
            "school discrimination",
            "student rights",
            "exam barred",
        ],
        "guidance": (
            "Keep admission documents, notices, fee receipts, results, and "
            "communications. Use the institution's written appeal or grievance "
            "process and consider contacting the education authority, "
            "ombudsman, legal-aid service, or lawyer."
        ),
    },
    {
        "category": "Police, Detention, and Due Process",
        "issue": "Possible unlawful detention, police abuse, or denial of due process",
        "keywords": [
            "police",
            "arrested",
            "detained",
            "custody",
            "beaten by police",
            "torture",
            "false case",
            "no lawyer",
            "illegal detention",
            "prison",
        ],
        "guidance": (
            "Record names, badge numbers, locations, times, witnesses, medical "
            "evidence, and case documents where safely possible. Seek urgent "
            "assistance from a criminal-defense lawyer, legal-aid provider, "
            "court, oversight body, or trusted human-rights organization."
        ),
    },
]

EMERGENCY_TERMS = [
    "immediate danger",
    "going to kill",
    "threatened to kill",
    "death threat",
    "weapon",
    "kidnapped",
    "abducted",
    "being attacked",
    "locked up",
    "bleeding",
    "suicide",
    "self harm",
    "self-harm",
]

HIGH_RISK_TERMS = [
    "violence",
    "assault",
    "rape",
    "torture",
    "detained",
    "arrested",
    "stalking",
    "domestic violence",
    "child abuse",
    "forced labor",
    "forced labour",
    "trafficking",
]


def human_rights_assistant(text: str) -> dict[str, Any]:
    normalized = " ".join(text.lower().split())

    best_rule = None
    best_score = 0
    matched_keywords: list[str] = []

    for rule in CATEGORY_RULES:
        matches = [
            keyword
            for keyword in rule["keywords"]
            if keyword in normalized
        ]

        if len(matches) > best_score:
            best_rule = rule
            best_score = len(matches)
            matched_keywords = matches

    emergency_matches = [
        term for term in EMERGENCY_TERMS if term in normalized
    ]

    high_risk_matches = [
        term for term in HIGH_RISK_TERMS if term in normalized
    ]

    if emergency_matches:
        priority = "Critical"
        urgent = True
    elif high_risk_matches:
        priority = "High"
        urgent = False
    elif best_score >= 2:
        priority = "Medium"
        urgent = False
    else:
        priority = "Low"
        urgent = False

    if best_rule is None:
        category = "General Human Rights Concern"
        issue = "A possible human-rights concern requiring further review"
        guidance = (
            "Write down the events in chronological order and preserve relevant "
            "documents, messages, photographs, notices, and witness details. "
            "Consider contacting a local legal-aid service, human-rights body, "
            "ombudsman, or qualified lawyer for advice specific to your location."
        )
    else:
        category = best_rule["category"]
        issue = best_rule["issue"]
        guidance = best_rule["guidance"]

    if urgent:
        safety_message = (
            "The description may indicate immediate danger. Move to a safe "
            "location if possible and contact local emergency services or a "
            "trusted person now. Do not confront a dangerous person or collect "
            "evidence when doing so could increase the risk."
        )
    else:
        safety_message = (
            "This assessment is general information, not a legal decision. "
            "Local law and available remedies depend on the country and facts."
        )

    confidence = min(95, 40 + best_score * 18) if best_rule else 30

    return {
        "category": category,
        "issue": issue,
        "priority": priority,
        "urgent": urgent,
        "confidence": confidence,
        "matched_keywords": matched_keywords,
        "guidance": guidance,
        "safety_message": safety_message,
    }
