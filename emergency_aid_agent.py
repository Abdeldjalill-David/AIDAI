"""
Emergency First Aid AI Agent System
Minimal, open-source, local models only (no APIs)
Runs on Google Colab with T4 GPU

Architecture:
1. Risk Classifier Agent -> outputs one-word classification
2. Content Retriever -> fetches from ChromaDB
3. First Aid Response Agent -> generates grounded response
4. Multi-turn conversation support

Install in Colab:
!pip install chromadb transformers torch sentence-transformers
"""

import chromadb
from chromadb.config import Settings
import torch
from transformers import pipeline
import json
from datetime import datetime

# ============================================================================
# STEP 1: INITIALIZE MODELS (runs once)
# ============================================================================

class EmergencyFirstAidAgent:
    def __init__(self):
        print("🚀 Initializing Emergency First Aid Agent System...")
        
        # Use small, efficient models for Colab T4
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Using device: {self.device}")
        
        # Initialize risk classifier (lightweight model)
        print("   Loading Risk Classifier...")
        self.classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased",
            device=0 if self.device == "cuda" else -1
        )
        
        # Initialize response generator (small model for speed)
        print("   Loading Response Generator...")
        self.generator = pipeline(
            "text-generation",
            model="distilgpt2",
            device=0 if self.device == "cuda" else -1
        )
        
        # Initialize sentence embedder for ChromaDB (matches content embedding)
        print("   Loading Sentence Embedder...")
        from sentence_transformers import SentenceTransformer
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        print("   Initializing ChromaDB...")
        self.chroma_client = chromadb.Client()
        self.knowledge_collection = None
        
        # Load skills
        self.class_skill = self._load_skill("CLASS_SKILL.md")
        self.first_aid_skill = self._load_skill("SKILL.md")
        
        # Conversation history for multi-turn
        self.conversation_history = []
        
        print("✅ Agent System Ready!\n")
    
    def _load_skill(self, filename):
        """Load skill file"""
        try:
            with open(filename, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Warning: {filename} not found")
            return ""
    
    # ========================================================================
    # STEP 2: SETUP CHROMADB WITH CONTENT
    # ========================================================================
    
    def setup_knowledge_base(self, content_file="content_corpus.md"):
        """
        Ingest content into ChromaDB for retrieval
        This needs to run once to populate the knowledge base
        """
        print("📚 Setting up Knowledge Base from content corpus...")
        
        # Load content
        try:
            with open(content_file, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ Error: {content_file} not found")
            return False
        
        # Split by major sections (each emergency type)
        sections = content.split("### ")[1:]  # Skip header
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, section in enumerate(sections):
            lines = section.split('\n')
            title = lines[0].strip()
            section_text = '\n'.join(lines[1:])
            
            documents.append(section_text[:500])  # Keep text manageable
            metadatas.append({
                "title": title,
                "type": "emergency_guidance",
                "section_number": idx
            })
            ids.append(f"section_{idx}")
        
        # Create collection and add documents
        self.knowledge_collection = self.chroma_client.get_or_create_collection(
            name="emergency_first_aid",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add documents to ChromaDB
        self.knowledge_collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✅ Loaded {len(documents)} emergency guidance sections into ChromaDB\n")
        return True
    
    # ========================================================================
    # STEP 3: RISK CLASSIFICATION (Agent 1)
    # ========================================================================
    
    def classify_risk(self, user_input):
        """
        Classify emergency type into ONE WORD category
        
        Categories: CARDIAC, RESPIRATORY, BLEEDING, TRAUMA, BURN, 
                   POISONING, NEUROLOGICAL, ALLERGIC, ABDOMINAL, 
                   PSYCHOLOGICAL, MINOR
        """
        print("🔍 Classifying Emergency Risk...")
        
        # Create classification prompt
        classification_prompt = f"""
        Based on the CLASS_SKILL.md guidelines, classify this emergency into ONE WORD ONLY.
        
        User said: "{user_input}"
        
        Valid categories: CARDIAC, RESPIRATORY, BLEEDING, TRAUMA, BURN, POISONING, 
                         NEUROLOGICAL, ALLERGIC, ABDOMINAL, PSYCHOLOGICAL, MINOR
        
        Return ONLY the category name. Nothing else.
        """
        
        # Use the classifier model
        try:
            # Create a simpler classification by checking keywords
            classification = self._keyword_classify(user_input)
            print(f"   Risk Classification: {classification}")
            return classification
        except Exception as e:
            print(f"   Error in classification: {e}")
            return "MINOR"
    
    def _keyword_classify(self, text):
        """
        Simple, deterministic keyword-based classification
        (More reliable for hackathon than fine-tuning models)
        """
        text_lower = text.lower()
        
        # CRITICAL/HIGH PRIORITY FIRST
        if any(word in text_lower for word in ['chest pain', 'heart attack', 'cardiac', 'heart', 'palpitation']):
            return "CARDIAC"
        
        if any(word in text_lower for word in ['choking', 'cannot breathe', 'no breathing', 'airway', 'asthma', 'anaphylaxis', 'allergic reaction']):
            return "RESPIRATORY"
        
        if any(word in text_lower for word in ['bleeding', 'hemorrhage', 'blood', 'wound', 'cut', 'laceration']):
            return "BLEEDING"
        
        if any(word in text_lower for word in ['fall', 'accident', 'crash', 'hit', 'injured', 'fracture', 'broken', 'sprain', 'head injury']):
            return "TRAUMA"
        
        if any(word in text_lower for word in ['burn', 'burned', 'fire', 'hot', 'chemical burn']):
            return "BURN"
        
        if any(word in text_lower for word in ['poison', 'overdose', 'took pills', 'ingested', 'toxic', 'drug']):
            return "POISONING"
        
        if any(word in text_lower for word in ['seizure', 'convulsion', 'stroke', 'unconscious', 'unresponsive', 'paralysis']):
            return "NEUROLOGICAL"
        
        if any(word in text_lower for word in ['allergy', 'sting', 'hives', 'swelling', 'reaction']):
            return "ALLERGIC"
        
        if any(word in text_lower for word in ['stomach', 'abdominal', 'belly pain', 'appendix']):
            return "ABDOMINAL"
        
        if any(word in text_lower for word in ['suicide', 'self-harm', 'mental', 'depressed', 'crisis', 'panic']):
            return "PSYCHOLOGICAL"
        
        return "MINOR"
    
    # ========================================================================
    # STEP 4: CONTENT RETRIEVAL (Agent 2)
    # ========================================================================
    
    def retrieve_content(self, risk_classification, user_input):
        """
        Retrieve relevant content from ChromaDB based on risk category
        """
        print("📖 Retrieving relevant content from knowledge base...")
        
        if not self.knowledge_collection:
            print("   ⚠️  Knowledge base not initialized. Using CLASS_SKILL guidelines only.")
            return self._get_category_guidelines(risk_classification)
        
        # Query ChromaDB for relevant documents
        try:
            results = self.knowledge_collection.query(
                query_texts=[f"{risk_classification} {user_input}"],
                n_results=3  # Top 3 most relevant sections
            )
            
            retrieved_text = ""
            if results['documents']:
                for doc in results['documents'][0]:
                    retrieved_text += doc + "\n\n"
            
            print(f"   Retrieved {len(results['documents'][0])} relevant sections")
            return retrieved_text
        
        except Exception as e:
            print(f"   Retrieval error: {e}")
            return self._get_category_guidelines(risk_classification)
    
    def _get_category_guidelines(self, category):
        """Extract relevant guidelines from CLASS_SKILL for this category"""
        if category in self.class_skill:
            start = self.class_skill.find(f"### {category}")
            if start != -1:
                end = self.class_skill.find("###", start + 1)
                if end == -1:
                    return self.class_skill[start:start+500]
                return self.class_skill[start:end]
        return "Standard emergency first aid applies. Call emergency services if in doubt."
    
    # ========================================================================
    # STEP 5: RESPONSE GENERATION (Agent 3)
    # ========================================================================
    
    def generate_response(self, user_input, classification, retrieved_content):
        """
        Generate first aid guidance using:
        - User input (emergency description)
        - Classification (risk type)
        - Retrieved content (evidence-based guidance)
        - SKILL.md (response structure guidelines)
        """
        print("💬 Generating First Aid Guidance...")
        
        # Build context from all sources
        context = f"""
You are an emergency first aid guide. Use ONLY the provided content - do NOT invent treatments.

Emergency Type: {classification}

User's Situation: {user_input}

Evidence-Based Guidelines:
{retrieved_content}

Response Structure (from SKILL.md):
{self._get_response_structure(classification)}

Generate a clear, step-by-step first aid response. CRITICAL: Do not hallucinate information.
Only use facts from the guidelines above. If information isn't in the guidelines, say so.
"""
        
        try:
            # Generate response using the model
            response = self.generator(
                context,
                max_length=300,
                num_return_sequences=1,
                temperature=0.5,
                do_sample=True
            )
            
            generated_text = response[0]['generated_text'].strip()
            
            # Clean up the response (remove context echo)
            if "User's Situation:" in generated_text:
                generated_text = generated_text.split("User's Situation:")[-1].strip()
            
            return generated_text
        
        except Exception as e:
            print(f"   Generation error: {e}")
            return self._create_fallback_response(classification)
    
    def _get_response_structure(self, classification):
        """Get appropriate response structure based on severity"""
        if classification in ["CARDIAC", "RESPIRATORY", "SEVERE BLEEDING", "NEUROLOGICAL"]:
            return """
IMMEDIATE ACTION: What to do right now
CALL EMERGENCY: 911/112/999 immediately  
POSITIONING: Safe recovery position
MONITORING: What signs to watch for
DO NOT: Critical mistakes to avoid
"""
        else:
            return """
ASSESSMENT: What to check
CARE STEPS: Numbered first aid actions
SEEK HELP: When to get professional care
MONITOR: Watch for these warning signs
"""
    
    def _create_fallback_response(self, classification):
        """Fallback if generation fails"""
        if classification in ["CARDIAC", "RESPIRATORY"]:
            return f"🚨 CRITICAL: Call emergency services (911/112) immediately. {classification} emergency detected."
        elif classification in ["TRAUMA", "BLEEDING", "BURN"]:
            return f"⚠️  URGENT: Seek emergency medical care. {classification} emergency - requires professional assessment."
        else:
            return f"Information on {classification} emergencies retrieved. Follow guidelines above."
    
    # ========================================================================
    # STEP 6: MULTI-TURN CONVERSATION
    # ========================================================================
    
    def process_input(self, user_input):
        """
        Main function: Process user input through full pipeline
        Supports multi-turn conversation
        """
        print("\n" + "="*70)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] User: {user_input}")
        print("="*70)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 1: Classify risk
        classification = self.classify_risk(user_input)
        
        # Step 2: Retrieve relevant content
        content = self.retrieve_content(classification, user_input)
        
        # Step 3: Generate response
        response = self.generate_response(user_input, classification, content)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "classification": classification,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"\n🏥 FIRST AID AGENT RESPONSE:\n{response}\n")
        
        return {
            "classification": classification,
            "response": response,
            "source_content": content[:200] + "..."
        }
    
    def get_conversation_history(self):
        """Return full conversation history"""
        return self.conversation_history
    
    def reset_conversation(self):
        """Reset for new emergency"""
        self.conversation_history = []
        print("🔄 Conversation reset for new emergency\n")


# ============================================================================
# STEP 7: GOOGLE COLAB INTERFACE
# ============================================================================

def run_in_colab():
    """
    Simple interactive interface for Google Colab
    """
    agent = EmergencyFirstAidAgent()
    
    # Setup knowledge base (one-time)
    agent.setup_knowledge_base("content_corpus.md")
    
    print("💬 Emergency First Aid Agent Ready for Chat")
    print("=" * 70)
    print("Type your emergency. Type 'history' to see conversation, 'reset' to start new emergency")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("\n🚨 Emergency Description: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("❌ Exiting Emergency First Aid System. Stay safe!")
                break
            
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                continue
            
            elif user_input.lower() == 'history':
                print("\n📋 Conversation History:")
                for msg in agent.get_conversation_history():
                    print(f"  [{msg['role'].upper()}] {msg['content'][:100]}...")
                continue
            
            # Process emergency
            result = agent.process_input(user_input)
        
        except KeyboardInterrupt:
            print("\n\n⏸️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


# ============================================================================
# QUICK START FOR COLAB
# ============================================================================

if __name__ == "__main__":
    # Uncomment below to run in Colab:
    # run_in_colab()
    
    # Or use programmatically:
    agent = EmergencyFirstAidAgent()
    agent.setup_knowledge_base("content_corpus.md")
    
    # Test example
    result = agent.process_input("My friend fell and has a severe head injury, not responding")
    print(f"\nClassification: {result['classification']}")
