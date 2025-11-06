# MedXM.ai - Fully Automated Medical Report Generator

**Complete End-to-End Solution: Audio Recording → Transcription → AI Report Generation → Professional Medical Documentation**

---

## 🎯 What This System Does

This is a **fully automated, HIPAA-compliant medical report generation system** that transforms audio recordings of doctor-patient consultations into professional medical/legal documentation.

### Complete Workflow

```
1. Record Audio
   ↓
2. Upload Audio File
   ↓
3. Automatic Transcription with Speaker Diarization
   (identifies Doctor vs Patient speech)
   ↓
4. AI-Powered Report Generation
   (transforms transcription into professional medical documentation)
   ↓
5. Professional Medical Report (Word Document)
```

---

## ✨ Key Features

### 🎙️ Audio Transcription
- **Two Options:**
  - **Local (Whisper.cpp)**: Free, offline, good accuracy (85-90%)
  - **Azure AI Speech**: Best accuracy (95-98%), cloud-based, requires BAA
- **Speaker Diarization**: Automatically identifies different speakers
- **HIPAA Compliant**: Full audit logging and secure file handling

### 📝 Report Generation
- **Two Options:**
  - **Local (Llama.cpp)**: Free, offline, local control
  - **Azure OpenAI GPT-4**: Best quality, cloud-based, requires API key
- **18+ Medical Specialties** supported
- **Comprehensive Report Sections**:
  - Accident Details
  - Initial & Current Complaints
  - Course of Treatment
  - Past Medical History
  - Clinical Examination
  - And 10+ more sections

### 🔒 HIPAA Compliance
- ✅ Audit logging for all PHI access
- ✅ Secure file deletion (overwrite before delete)
- ✅ Encrypted output storage
- ✅ User tracking and encounter linking
- ✅ BAA verification for cloud services
- ✅ Local processing option (no cloud required)

### 💰 Cost Flexibility
- **FREE Option**: 100% local processing (whisper.cpp + llama.cpp)
- **Hybrid Option**: Mix local and cloud based on needs
- **Cloud Option**: Azure AI for best accuracy (~$1/hour audio + $0.03/1K tokens)

---

## 📦 What's Included

### Part 1: MedXM.ai Web Application (Next.js)
- Modern web interface
- User authentication
- Report library and management
- Document generation (Microsoft Word)
- Database storage (MongoDB)

### Part 2: ComfyUI Audio Transcription Nodes
- Local whisper.cpp transcription
- Azure AI Speech transcription
- Speaker diarization
- HIPAA compliance features
- Secure deletion tools

### Part 3: Integrated APIs
- Audio transcription API (both local and Azure)
- Report generation API (both local and Azure OpenAI)
- Audit logging system
- Secure file handling

---

## 🚀 Installation

### Prerequisites

**Required:**
- Node.js 18+
- MongoDB (local or Atlas)

**Optional (for local AI):**
- Whisper.cpp (for local audio transcription)
- Llama.cpp (for local report generation)

**Optional (for cloud AI):**
- Azure account with Speech Service (requires BAA for HIPAA)
- Azure OpenAI API key

### Step 1: Clone and Install

```bash
# Clone repository
git clone <your-repo-url>
cd medxm-ai

# Install dependencies
npm install
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**For Cloud AI (Azure):**
```env
OPENAI_API_KEY=your_azure_openai_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastus
MONGODB_URI=mongodb://localhost:27017/medxm
```

**For Local AI:**
```env
WHISPER_BIN=/models/audio/whisper.cpp
WHISPER_MODEL=/models/audio/ggml-base.en.bin
LLAMA_BIN=/models/llm/llama
LLAMA_MODEL=/models/llm/mistral-7b-instruct-v0.1.Q4_0.gguf
MONGODB_URI=mongodb://localhost:27017/medxm
```

### Step 3: Set Up AI Models

#### Option A: Local AI Setup

**Install Whisper.cpp:**
```bash
# Clone and compile whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make

# Download model
bash ./models/download-ggml-model.sh base.en

# Move to standard location
sudo mkdir -p /models/audio
sudo cp main /models/audio/whisper.cpp
sudo cp models/ggml-base.en.bin /models/audio/
```

**Install Llama.cpp:**
```bash
# Clone and compile llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Download a medical-focused model
# Example: Mistral 7B Instruct
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf

# Move to standard location
sudo mkdir -p /models/llm
sudo cp main /models/llm/llama
sudo cp mistral-7b-instruct-v0.1.Q4_0.gguf /models/llm/
```

#### Option B: Cloud AI Setup

**Azure Speech Service:**
1. Sign in to https://portal.azure.com
2. Create Speech Service resource
3. Get API key and region
4. **IMPORTANT**: Sign BAA with Microsoft for HIPAA compliance
5. See `ComfyUI-llama-cpp-cli/AZURE_HIPAA_SETUP.md` for details

**Azure OpenAI:**
1. Get Azure OpenAI access
2. Deploy GPT-4 model
3. Get API key and endpoint
4. Configure in .env

### Step 4: Set Up HIPAA Directories

```bash
# Create secure directories
sudo mkdir -p /secure/phi_audio
sudo mkdir -p /secure/transcriptions
sudo chmod 700 /secure
sudo chmod 700 /secure/phi_audio
sudo chmod 700 /secure/transcriptions

# Create audit log
sudo touch /secure/phi_audit.log
sudo chmod 600 /secure/phi_audit.log
```

### Step 5: Start the Application

```bash
# Start MongoDB (if local)
mongod

# Start development server
npm run dev

# Open browser
# http://localhost:3000
```

---

## 📖 Usage Guide

### 1. Create Account
- Navigate to http://localhost:3000
- Click "Create Account"
- Enter your details and specialty
- Login

### 2. Generate Report with Audio

**Step 2.1: Upload Audio**
- Click "Generate New Report"
- Configure report settings (title, claimant info, specialty)
- For each section, choose "Upload Audio"
- Select audio file (WAV, MP3, etc.)
- Choose transcription provider:
  - **Local**: Free, offline (whisper.cpp)
  - **Azure**: Best accuracy (requires BAA)
- Set number of speakers (e.g., 2 for doctor + patient)

**Step 2.2: Auto-Transcribe**
- System transcribes audio automatically
- Speaker diarization identifies different speakers
- Transcription appears with speaker labels

**Step 2.3: Generate Report Content**
- Choose report generation provider:
  - **Local**: Free, offline (llama.cpp)
  - **Azure OpenAI**: Best quality (GPT-4)
- Click "Generate Content"
- AI transforms transcription into professional medical narrative
- Review and refine if needed

**Step 2.4: Complete All Sections**
- Repeat for all report sections
- System saves progress automatically

**Step 2.5: Process and Download**
- Click "Finish & Process Report"
- System generates Microsoft Word document
- Download professional medical report

### 3. View Report Library
- Access all your generated reports
- Download, view, or delete reports
- Full audit trail maintained

---

## 🔧 API Endpoints

### Audio Transcription

**POST /api/transcribe**

Upload audio for transcription with speaker diarization.

```javascript
// Request
const formData = new FormData();
formData.append('audio', audioFile);
formData.append('provider', 'local'); // or 'azure'
formData.append('language', 'en');
formData.append('numSpeakers', '2');
formData.append('userId', 'dr_smith');
formData.append('encounterId', 'ENC123456');
formData.append('baaConfirmed', 'true'); // for Azure

// Response
{
  "success": true,
  "provider": "local",
  "transcription": "Full transcription text...",
  "diarized_text": "[Speaker 1] Hello...\n[Speaker 2] Hi...",
  "security_info": {
    "audit_logged": true,
    "user_id": "dr_smith",
    "temp_file_deleted": true
  }
}
```

### Report Generation (Local)

**POST /api/generate-local**

Generate report content using local llama.cpp.

```javascript
// Request
{
  "sectionId": "accident_details",
  "inputMethod": "audio-upload",
  "inputData": "Transcribed text here...",
  "config": {
    "specialtyType": "Orthopedic Surgery",
    "claimantGender": "male",
    "perspective": "first"
  }
}

// Response
{
  "content": "Professional medical narrative...",
  "provider": "local",
  "model": "/models/llm/mistral-7b-instruct-v0.1.Q4_0.gguf"
}
```

### Report Generation (Cloud)

**POST /api/generate**

Generate report content using Azure OpenAI GPT-4.

```javascript
// Same request format as generate-local
// Response includes Azure OpenAI generated content
```

---

## 🏥 HIPAA Compliance

### For Healthcare Use

**CRITICAL Requirements:**

1. **Azure AI (Cloud)**:
   - ✅ Sign Business Associate Agreement (BAA) with Microsoft
   - ✅ Use HIPAA-eligible Azure regions (US regions)
   - ✅ Enable audit logging
   - ✅ Configure access controls
   - See: `ComfyUI-llama-cpp-cli/AZURE_HIPAA_SETUP.md`

2. **Local AI**:
   - ✅ No BAA required (100% on-premise)
   - ✅ Enable audit logging
   - ✅ Secure file permissions
   - ✅ Network isolation
   - See: `ComfyUI-llama-cpp-cli/HIPAA_COMPLIANCE.md`

### Security Features

- **Audit Logging**: All PHI access logged with WHO, WHAT, WHEN, WHERE
- **Secure Deletion**: Files overwritten before deletion (DoD 5220.22-M)
- **Encryption**: Output files encrypted and access-controlled
- **User Tracking**: All operations linked to user ID and encounter ID
- **BAA Verification**: System enforces BAA confirmation for cloud processing

### Audit Log Format

```json
{
  "timestamp": "2025-11-06T16:30:00.000Z",
  "event_type": "AZURE_TRANSCRIBE_START",
  "user_id": "dr_smith",
  "file_identifier": "a3b5c7d9e1f2g3h4",
  "details": "Provider: azure, Encounter: ENC123456, Speakers: 2"
}
```

---

## 💡 Usage Patterns

### Pattern 1: Cloud-Only (Best Accuracy)
**Use when:** Need best quality, low volume
```
Audio → Azure Speech → Azure OpenAI → Report
Cost: ~$1/hour + $0.03/1K tokens
```

### Pattern 2: Local-Only (Zero Cost)
**Use when:** High volume, cost-sensitive, maximum privacy
```
Audio → Whisper.cpp → Llama.cpp → Report
Cost: $0 (after setup)
```

### Pattern 3: Hybrid (Best Value)
**Use when:** Want flexibility
```
Important Cases:
Audio → Azure Speech → Azure OpenAI → Report

Routine Cases:
Audio → Whisper.cpp → Llama.cpp → Report
```

---

## 📂 Project Structure

```
medxm-ai/
├── app/
│   ├── api/
│   │   ├── transcribe/          # Audio transcription API
│   │   ├── generate/            # Cloud report generation (Azure OpenAI)
│   │   ├── generate-local/      # Local report generation (Llama.cpp)
│   │   ├── auth/                # Authentication
│   │   ├── reports/             # Report management
│   │   └── refine/              # Content refinement
│   ├── dashboard/               # User dashboard
│   ├── library/                 # Report library
│   └── report/                  # Report generation UI
├── ComfyUI-llama-cpp-cli/       # Audio transcription nodes
│   ├── audio_transcribe.py      # Local transcription
│   ├── audio_transcribe_azure.py # Azure transcription
│   ├── HIPAA_COMPLIANCE.md      # HIPAA documentation
│   ├── AZURE_HIPAA_SETUP.md     # Azure setup guide
│   └── QUICK_START.md           # Quick start guide
├── lib/
│   └── mongodb.ts               # Database connection
├── .env.example                 # Environment template
└── package.json                 # Dependencies
```

---

## 🔍 Troubleshooting

### Audio Transcription Issues

**"Whisper.cpp binary not found"**
```bash
# Install whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp && make
sudo cp main /models/audio/whisper.cpp
```

**"Azure Speech Key invalid"**
- Verify key in Azure Portal
- Check region matches (e.g., "eastus")
- Ensure BAA is signed for HIPAA

### Report Generation Issues

**"Llama.cpp binary not found"**
```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make
sudo cp main /models/llm/llama
```

**"OpenAI API error"**
- Verify API key is correct
- Check account has credits
- Ensure GPT-4 access is enabled

### HIPAA Compliance Issues

**"Audit logging failed"**
```bash
# Create secure directory
sudo mkdir -p /secure
sudo chmod 700 /secure
sudo touch /secure/phi_audit.log
sudo chmod 600 /secure/phi_audit.log
```

---

## 📚 Documentation

- **Main README**: This file
- **Quick Start**: `ComfyUI-llama-cpp-cli/QUICK_START.md`
- **HIPAA Compliance**: `ComfyUI-llama-cpp-cli/HIPAA_COMPLIANCE.md`
- **Azure Setup**: `ComfyUI-llama-cpp-cli/AZURE_HIPAA_SETUP.md`
- **Audio Transcription**: `ComfyUI-llama-cpp-cli/AUDIO_TRANSCRIPTION_SETUP.md`
- **Original MedXM README**: `README.md`

---

## 🚀 Next Steps

1. **Install the system** following steps above
2. **Choose your AI providers** (local, cloud, or both)
3. **Configure HIPAA compliance** if processing PHI
4. **Test with non-PHI data** first
5. **Get legal/compliance approval** for healthcare use
6. **Train staff** on system usage
7. **Deploy for production** use

---

## ⚠️ Important Notes

### For Healthcare Use

- **Local AI**: No BAA required, 100% on-premise
- **Azure AI**: Requires signed BAA with Microsoft
- **Always enable audit logging** for HIPAA compliance
- **Test thoroughly** with non-PHI data first
- **Get legal review** before processing real PHI
- **Document all procedures** and train staff

### Cost Considerations

| Scenario | Volume | Best Option | Monthly Cost |
|----------|--------|-------------|--------------|
| Small Clinic | <50 hrs | Azure AI | ~$50 |
| Medium Clinic | 50-200 hrs | Hybrid | $0-$200 |
| Large Hospital | >500 hrs | Local AI | $0 |

---

## 📞 Support

For technical issues:
- Check troubleshooting section above
- Review documentation in `ComfyUI-llama-cpp-cli/`
- Check environment variables in `.env`

For HIPAA compliance:
- Consult your healthcare compliance officer
- Review `HIPAA_COMPLIANCE.md`
- Consult healthcare attorney

---

## 📄 License

Proprietary - All rights reserved

---

**You now have a complete, HIPAA-compliant, fully automated medical report generation system!**

Choose local for cost savings and maximum privacy, or cloud for best accuracy. Or use both for maximum flexibility.
