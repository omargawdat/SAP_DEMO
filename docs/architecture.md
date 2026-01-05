# PII Shield - Architecture Diagrams

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph Input["📥 Input Sources"]
        TEXT[Text Input]
        CSV[CSV Files]
        JSON[JSON Files]
    end

    subgraph API["🌐 FastAPI Service"]
        DETECT["/detect"]
        ANON["/anonymize"]
        PROCESS["/process"]
        HEALTH["/health"]
    end

    subgraph Core["⚙️ PII Shield Core"]
        direction TB
        PREPROCESS["Preprocessing<br/>Unicode NFC + Whitespace"]

        subgraph Detectors["🔍 Detection Layer"]
            direction LR
            RULE["Rule-Based<br/>Email, Phone, IBAN<br/>German ID, CC, IP"]
            ML["ML/NER<br/>Presidio + spaCy<br/>Names, Addresses"]
            LLM["LLM Validator<br/>Claude API<br/>Context Analysis"]
        end

        DEDUP["Deduplication<br/>Highest Confidence Wins"]

        subgraph Strategies["🛡️ Anonymization"]
            direction LR
            REDACT["Redaction<br/>[EMAIL]"]
            MASK["Masking<br/>han***com"]
            HASH["Hashing<br/>SHA-256"]
        end
    end

    subgraph Output["📤 Output"]
        RESULT["Processed Text"]
        REPORT["Detection Report"]
        METRICS["Metrics & Stats"]
    end

    TEXT --> API
    CSV --> API
    JSON --> API

    API --> PREPROCESS
    PREPROCESS --> Detectors
    RULE --> DEDUP
    ML --> DEDUP
    LLM --> DEDUP
    DEDUP --> Strategies
    Strategies --> Output

    style Input fill:#e1f5fe
    style API fill:#fff3e0
    style Core fill:#f3e5f5
    style Output fill:#e8f5e9
```

---

## 2. Detection Pipeline Flow

```mermaid
flowchart LR
    subgraph Input
        A["Raw Text<br/>'Contact Hans at hans@sap.com'"]
    end

    subgraph Preprocessing
        B["Normalize Unicode<br/>Collapse Whitespace"]
    end

    subgraph Detection["Parallel Detection"]
        direction TB
        C1["📧 EmailDetector<br/>RFC 5322 Regex"]
        C2["📞 PhoneDetector<br/>German Formats"]
        C3["🏦 IBANDetector<br/>MOD-97 Checksum"]
        C4["🪪 GermanIDDetector<br/>Check Digit"]
        C5["💳 CreditCardDetector<br/>Luhn Algorithm"]
        C6["🌐 IPDetector<br/>IPv4/IPv6"]
        C7["🤖 PresidioDetector<br/>spaCy German NER"]
    end

    subgraph Aggregation
        D["Collect All Matches<br/>Sort by Position"]
    end

    subgraph Deduplication
        E["Group by (start, end)<br/>Keep Highest Confidence"]
    end

    subgraph Output
        F["List[PIIMatch]<br/>Ready for Strategy"]
    end

    A --> B --> Detection
    C1 & C2 & C3 & C4 & C5 & C6 & C7 --> D
    D --> E --> F

    style Input fill:#ffebee
    style Preprocessing fill:#fff8e1
    style Detection fill:#e3f2fd
    style Aggregation fill:#f3e5f5
    style Deduplication fill:#e8f5e9
    style Output fill:#e0f2f1
```

---

## 3. PIIMatch Data Model

```mermaid
classDiagram
    class PIIType {
        <<enumeration>>
        EMAIL
        PHONE
        IBAN
        CREDIT_CARD
        GERMAN_ID
        IP_ADDRESS
        NAME
        ADDRESS
        DATE_OF_BIRTH
        UNKNOWN
    }

    class PIIMatch {
        +PIIType type
        +str text
        +int start
        +int end
        +float confidence
        +str detector
        +length() int
        +overlaps(other) bool
    }

    class DetectionResult {
        +str original_text
        +List~PIIMatch~ matches
        +float processing_time_ms
        +has_pii() bool
        +pii_count() int
        +get_matches_by_type() dict
        +to_dict() dict
    }

    class ProcessingReport {
        +str original_text
        +str processed_text
        +List~PIIMatch~ matches
        +float processing_time_ms
        +pii_found() bool
        +count_by_type() dict
        +to_json() str
    }

    PIIMatch --> PIIType
    DetectionResult --> PIIMatch
    ProcessingReport --> PIIMatch
```

---

## 4. Detector Class Hierarchy

```mermaid
classDiagram
    class Detector {
        <<abstract>>
        +detect(text: str) List~PIIMatch~*
    }

    class EmailDetector {
        -PATTERN: regex
        +detect(text) List~PIIMatch~
    }

    class PhoneDetector {
        -GERMAN_PATTERNS: list
        -MOBILE_PREFIXES: set
        +detect(text) List~PIIMatch~
        -calculate_confidence() float
    }

    class IBANDetector {
        -COUNTRY_LENGTHS: dict
        +detect(text) List~PIIMatch~
        -validate_checksum(iban) bool
    }

    class GermanIDDetector {
        -VALID_PREFIXES: set
        -WEIGHTS: tuple
        +detect(text) List~PIIMatch~
        -validate_check_digit(id) bool
    }

    class CreditCardDetector {
        +detect(text) List~PIIMatch~
        -luhn_validate(number) bool
    }

    class IPAddressDetector {
        +detect(text) List~PIIMatch~
        -validate_ipv4(ip) bool
        -validate_ipv6(ip) bool
    }

    class PresidioDetector {
        -analyzer: AnalyzerEngine
        -nlp_engine: SpacyNlpEngine
        +detect(text) List~PIIMatch~
    }

    class LLMValidator {
        -client: Anthropic
        -model: str
        +validate_matches(text, matches) List~PIIMatch~
        -batch_sentences(matches) List
    }

    Detector <|-- EmailDetector
    Detector <|-- PhoneDetector
    Detector <|-- IBANDetector
    Detector <|-- GermanIDDetector
    Detector <|-- CreditCardDetector
    Detector <|-- IPAddressDetector
    Detector <|-- PresidioDetector
    Detector <|-- LLMValidator
```

---

## 5. Strategy Class Hierarchy

```mermaid
classDiagram
    class Strategy {
        <<abstract>>
        +apply(text: str, matches: List~PIIMatch~) str*
    }

    class RedactionStrategy {
        -placeholder_format: str
        +apply(text, matches) str
    }

    class MaskingStrategy {
        -mask_char: str
        -visible_chars: int
        +apply(text, matches) str
        -mask_value(value) str
    }

    class HashingStrategy {
        -salt: str
        -length: int
        +apply(text, matches) str
        -hash_value(value) str
    }

    Strategy <|-- RedactionStrategy
    Strategy <|-- MaskingStrategy
    Strategy <|-- HashingStrategy

    note for RedactionStrategy "Output: [EMAIL], [PHONE], [NAME]"
    note for MaskingStrategy "Output: han***com, +49***678"
    note for HashingStrategy "Output: a3f2b1c4d9e8f7a6"
```

---

## 6. Human-in-the-Loop Workflow

```mermaid
flowchart TB
    subgraph Step1["Step 1: Input & Detection"]
        A[User Enters Text] --> B[Select LLM Model]
        B --> C[Set Confidence Threshold]
        C --> D["🔍 Analyze Text"]
        D --> E["/api/v1/detect"]
    end

    subgraph Step2["Step 2: Review & Approve"]
        E --> F{Confidence >= Threshold?}
        F -->|Yes| G["✅ Auto-Approved<br/>(High Confidence)"]
        F -->|No| H["⚠️ Needs Review<br/>(Low Confidence)"]
        H --> I{User Decision}
        I -->|Confirm| J["✓ Is PII"]
        I -->|Reject| K["✗ Not PII"]
        G --> L[Select Strategy]
        J --> L
    end

    subgraph Step3["Step 3: Anonymization"]
        L --> M["🛡️ Apply Strategy"]
        M --> N["/api/v1/anonymize"]
        N --> O["📄 Processed Text"]
        N --> P["📊 Analytics Report"]
    end

    style Step1 fill:#e3f2fd
    style Step2 fill:#fff3e0
    style Step3 fill:#e8f5e9
```

---

## 7. LLM Validation Flow

```mermaid
flowchart TB
    A[Detection Results] --> B{Split by Confidence}

    B -->|>= 90%| C["✅ Auto-Approved<br/>Skip LLM"]
    B -->|< 90%| D["⚠️ Low Confidence<br/>Send to LLM"]

    D --> E["Extract Sentences<br/>Group Matches"]
    E --> F["Batch 10 Sentences<br/>Per API Call"]
    F --> G["Claude API<br/>(haiku/sonnet/opus)"]

    G --> H{LLM Response}
    H -->|is_pii: true| I["✅ Validated<br/>Update Confidence"]
    H -->|is_pii: false| J["❌ Rejected<br/>False Positive"]

    C --> K[Final Matches]
    I --> K
    J --> L[Filtered Out]

    style C fill:#c8e6c9
    style I fill:#c8e6c9
    style J fill:#ffcdd2
    style L fill:#ffcdd2
```

---

## 8. API Request/Response Flow

```mermaid
sequenceDiagram
    participant U as User/Client
    participant A as FastAPI
    participant P as TextProcessor
    participant D as Detectors
    participant L as LLM Validator
    participant S as Strategy

    U->>A: POST /detect {text, use_llm}
    A->>P: process(text)
    P->>D: detect(text) [parallel]
    D-->>P: List[PIIMatch]

    alt use_llm = true
        P->>L: validate_low_confidence(matches)
        L-->>P: validated matches
    end

    P-->>A: DetectionResult
    A-->>U: {matches, summary, time_ms}

    U->>U: Review matches (Human-in-the-Loop)

    U->>A: POST /anonymize {text, matches, strategy}
    A->>S: apply(text, matches)
    S-->>A: processed_text
    A-->>U: {original, processed, summary}
```

---

## 9. Deployment Architecture

```mermaid
flowchart TB
    subgraph Developer["👨‍💻 Developer"]
        CODE[Code Changes]
    end

    subgraph GitHub["GitHub"]
        REPO[Repository]
        ACTIONS[GitHub Actions]
    end

    subgraph CI["CI/CD Pipeline"]
        LINT[Ruff Lint]
        TEST[Pytest]
        BUILD[Docker Build]
    end

    subgraph AWS["☁️ AWS Cloud"]
        ECR[ECR Registry]

        subgraph AppRunner["App Runner"]
            API_SVC["API Service<br/>:8000"]
            UI_SVC["Streamlit UI<br/>:8501"]
        end

        SECRETS[Secrets Manager<br/>ANTHROPIC_API_KEY]
    end

    subgraph Users["🌍 Users"]
        BROWSER[Web Browser]
    end

    CODE --> REPO
    REPO --> ACTIONS
    ACTIONS --> LINT --> TEST --> BUILD
    BUILD --> ECR
    ECR --> AppRunner
    SECRETS --> API_SVC
    BROWSER --> UI_SVC
    UI_SVC --> API_SVC

    style Developer fill:#e1f5fe
    style GitHub fill:#f5f5f5
    style CI fill:#fff3e0
    style AWS fill:#fff8e1
    style Users fill:#e8f5e9
```

---

## 10. German PII Detection Examples

```mermaid
flowchart LR
    subgraph Input["German Text Examples"]
        T1["hans.mueller@sap.com"]
        T2["+49 30 12345678"]
        T3["DE89370400440532013000"]
        T4["L01X00T471"]
        T5["192.168.1.1"]
    end

    subgraph Detection["Detection & Validation"]
        D1["📧 Email<br/>RFC 5322 ✓"]
        D2["📞 Phone<br/>+49 Format ✓"]
        D3["🏦 IBAN<br/>MOD-97 ✓"]
        D4["🪪 German ID<br/>Check Digit ✓"]
        D5["🌐 IP Address<br/>IPv4 Valid ✓"]
    end

    subgraph Output["Redaction Output"]
        O1["[EMAIL]"]
        O2["[PHONE]"]
        O3["[IBAN]"]
        O4["[GERMAN_ID]"]
        O5["[IP_ADDRESS]"]
    end

    T1 --> D1 --> O1
    T2 --> D2 --> O2
    T3 --> D3 --> O3
    T4 --> D4 --> O4
    T5 --> D5 --> O5

    style Input fill:#ffebee
    style Detection fill:#e3f2fd
    style Output fill:#e8f5e9
```

---

## 11. Confidence Scoring System

```mermaid
flowchart TB
    subgraph Detectors["Detection Confidence"]
        E["Email: 1.0<br/>(Pattern match)"]
        P["Phone: 0.8-1.0<br/>(Format quality)"]
        I["IBAN: 0.7-1.0<br/>(Checksum valid?)"]
        G["German ID: 0.6-1.0<br/>(Check digit valid?)"]
        PR["Presidio: 0.0-1.0<br/>(NER confidence)"]
    end

    subgraph Threshold["Confidence Threshold"]
        T{">= 0.85?"}
    end

    subgraph Decision["Human-in-the-Loop"]
        HIGH["✅ Auto-Approve"]
        LOW["⚠️ Needs Review"]
    end

    subgraph LLM["Optional LLM Validation"]
        VAL["Claude validates<br/>context & semantics"]
        ADJ["Adjust confidence<br/>or reject"]
    end

    E & P & I & G & PR --> T
    T -->|Yes| HIGH
    T -->|No| LOW
    LOW --> VAL --> ADJ

    style HIGH fill:#c8e6c9
    style LOW fill:#fff3e0
    style LLM fill:#e3f2fd
```

---

## How to View These Diagrams

### Option 1: GitHub README
Copy any diagram to your `README.md` - GitHub renders Mermaid automatically.

### Option 2: Mermaid Live Editor
Visit [mermaid.live](https://mermaid.live) and paste the code.

### Option 3: VS Code Extension
Install "Mermaid Preview" extension for live rendering.

### Option 4: Export to PNG/SVG
Use mermaid-cli: `mmdc -i architecture.md -o diagram.png`
