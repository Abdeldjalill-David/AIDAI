# Emergency Risk Classification Skill

## Purpose
Classify incoming emergency messages into a single-word category for content routing.

## Classification Categories

### 1. **CARDIAC**
- Heart attacks, chest pain, palpitations, arrhythmias
- Sudden loss of consciousness without trauma
- Severe shortness of breath (cardiac origin)

### 2. **RESPIRATORY**
- Choking, airway obstruction
- Severe asthma attacks, anaphylaxis
- Difficulty breathing from non-cardiac causes
- Suspected poisoning/gas inhalation

### 3. **BLEEDING**
- Severe uncontrolled bleeding, hemorrhage
- Penetrating wounds, lacerations
- Internal bleeding signs (bruising, pain)
- Head wounds with bleeding

### 4. **TRAUMA**
- Falls, accidents, impact injuries
- Fractures, dislocations, sprains
- Head trauma, spinal injury concerns
- Crush injuries

### 5. **BURN**
- Thermal, chemical, or electrical burns
- Severity assessment (1st-3rd degree)
- Large area burns (>10% body surface)

### 6. **POISONING**
- Suspected ingestion of toxins/drugs
- Chemical exposure
- Overdose situations
- Corrosive substance ingestion

### 7. **NEUROLOGICAL**
- Seizures, convulsions, loss of consciousness
- Stroke symptoms (facial drooping, slurred speech)
- Severe headache with stiff neck
- Altered mental status

### 8. **ALLERGIC**
- Anaphylaxis, severe allergic reactions
- Hives, swelling, difficulty breathing from allergies
- Insect sting/bite reactions

### 9. **ABDOMINAL**
- Severe abdominal pain, appendicitis signs
- Vomiting blood, severe constipation
- Signs of peritonitis

### 10. **PSYCHOLOGICAL**
- Suicide risk assessment
- Self-harm, mental health crisis
- Panic attacks, severe anxiety
- Violent behavior assessment

### 11. **MINOR**
- Small cuts, minor bumps
- Mild pain without complications
- General health questions
- Preventive care inquiries

## Classification Rules

**CRITICAL (Immediate):** CARDIAC, RESPIRATORY, SEVERE BLEEDING, TRAUMA (head/spinal), NEUROLOGICAL, ANAPHYLAXIS
- Response priority: HIGHEST
- Recommend: Call emergency services (ambulance/911)

**URGENT (Within minutes):** BURN, POISONING, SEVERE ALLERGIC, ABDOMINAL (severe)
- Response priority: HIGH
- Recommend: Seek professional help immediately

**MODERATE:** PSYCHOLOGICAL, MINOR TRAUMA
- Response priority: MEDIUM
- Recommend: Professional assessment when possible

## Example Classifications

| Input | Category | Rationale |
|-------|----------|-----------|
| "My friend is not breathing" | RESPIRATORY | Airway emergency |
| "Bad cut on my arm, won't stop bleeding" | BLEEDING | Hemorrhage control needed |
| "I fell down stairs, head hurts" | TRAUMA | Impact injury with potential head injury |
| "Chest pain and shortness of breath" | CARDIAC | Classic heart attack signs |
| "I think I took too many pills" | POISONING | Overdose/toxin ingestion |
| "My hand is burned from the stove" | BURN | Thermal injury |
| "I'm having suicidal thoughts" | PSYCHOLOGICAL | Mental health crisis |
| "Small cut from paper" | MINOR | Non-emergency |

## Output Format
**Return ONLY the category name in one word** (e.g., "CARDIAC", "RESPIRATORY", "MINOR")

No explanation, no secondary categories, just the primary classification.

## Confidence Notes
- If ambiguous between two categories, default to the more life-threatening category
- If input is unclear, default to "TRAUMA" (safest assumption)
- Always err on the side of higher severity for emergency classification

## Source
Based on international emergency medicine guidelines (ACEP, EMS protocols)
Last updated: 2024
