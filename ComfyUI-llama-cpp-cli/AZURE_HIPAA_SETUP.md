# Azure AI HIPAA-Compliant Audio Transcription Setup

This guide explains how to set up Microsoft Azure AI Speech Service for HIPAA-compliant audio transcription with speaker diarization.

---

## ⚠️ CRITICAL: Business Associate Agreement (BAA) Required

**YOU MUST SIGN A BAA WITH MICROSOFT BEFORE PROCESSING PHI**

### What is a BAA?

A Business Associate Agreement (BAA) is a legal contract required by HIPAA when a third party (Microsoft) will handle Protected Health Information (PHI) on your behalf.

### How to Sign BAA with Microsoft

1. **For Enterprise Customers:**
   - Visit: https://aka.ms/BAA
   - Contact Microsoft Enterprise Support
   - Request HIPAA BAA for Azure Services
   - Legal teams will execute the agreement

2. **For Microsoft 365/Azure Customers:**
   - Sign in to Microsoft Service Trust Portal: https://servicetrust.microsoft.com/
   - Navigate to Compliance Manager
   - Download and sign the BAA
   - Return to Microsoft

3. **Verify BAA Coverage:**
   - Ensure your Azure subscription is covered
   - Verify Azure Speech Service is included
   - Document BAA execution date
   - Keep copy for compliance records

**⚠️ DO NOT process PHI without a signed BAA - this is a HIPAA violation!**

---

## Azure Setup Steps

### Step 1: Create Azure Account

1. **Sign up for Azure:**
   - Visit: https://azure.microsoft.com
   - Click "Start free" or "Sign in"
   - Complete account creation

2. **Choose appropriate subscription:**
   - Enterprise Agreement (for hospitals/large organizations)
   - Pay-As-You-Go (for small clinics)
   - Ensure HIPAA compliance is available for your subscription type

### Step 2: Sign Business Associate Agreement

**CRITICAL: Complete this before processing any PHI**

1. Contact Microsoft to sign BAA
2. Wait for BAA execution confirmation
3. Document BAA in your compliance records
4. Only then proceed with PHI processing

### Step 3: Create Azure Speech Service Resource

1. **Sign in to Azure Portal:**
   - Go to: https://portal.azure.com

2. **Create Speech Service Resource:**
   ```
   1. Click "Create a resource"
   2. Search for "Speech"
   3. Click "Speech" (by Microsoft)
   4. Click "Create"
   ```

3. **Configure Resource:**
   - **Subscription:** Choose your subscription
   - **Resource Group:** Create new (e.g., "healthcare-phi-resources")
   - **Region:** Choose HIPAA-eligible US region:
     - East US
     - East US 2
     - West US
     - West US 2
     - Central US
     - North Central US
     - South Central US
     - West Central US
   - **Name:** e.g., "healthcare-speech-service"
   - **Pricing tier:** S0 (Standard)

4. **Click "Review + create"**

5. **Click "Create"**

### Step 4: Get Your Azure Credentials

1. **Navigate to your Speech resource:**
   - Azure Portal → Resource Groups → Your resource group
   - Click on your Speech service

2. **Get Keys and Endpoint:**
   - Click "Keys and Endpoint" in left menu
   - Copy **KEY 1** (keep this secret!)
   - Note the **Region** (e.g., "eastus")

3. **Secure Your Keys:**
   ```bash
   # NEVER commit keys to git
   # NEVER share keys publicly
   # Store in environment variables or secure key vault
   ```

### Step 5: Configure HIPAA Compliance Settings

1. **Enable Encryption:**
   - Encryption in transit: Automatically enabled (TLS 1.2+)
   - Encryption at rest: Automatically enabled

2. **Configure Data Residency:**
   - Ensure data stays in chosen region
   - No cross-region data transfer

3. **Set Data Retention:**
   - Configure "No data retention" for PHI
   - Azure Portal → Speech Service → Configuration
   - Disable audio logging
   - Disable telemetry for PHI

4. **Enable Diagnostic Logging:**
   - Azure Portal → Speech Service → Diagnostic settings
   - Create diagnostic setting
   - Log to secure storage account
   - Enable audit logs

### Step 6: Configure Access Controls

1. **Set up Azure Active Directory:**
   - Use Azure AD for user authentication
   - Enable Multi-Factor Authentication (MFA)
   - Create security groups for healthcare roles

2. **Configure Role-Based Access Control (RBAC):**
   ```
   Roles to create:
   - Healthcare-Admin (full access)
   - Healthcare-Clinician (transcription access)
   - Healthcare-Compliance (read-only audit access)
   ```

3. **Assign Roles:**
   - Azure Portal → Speech Service → Access control (IAM)
   - Add role assignments
   - Use principle of least privilege

### Step 7: Install Azure SDK

```bash
# Install Azure Speech SDK
pip install azure-cognitiveservices-speech

# Verify installation
python -c "import azure.cognitiveservices.speech; print('Azure SDK installed!')"
```

### Step 8: Test Configuration (Non-PHI First!)

**IMPORTANT: Test with non-PHI audio first!**

```python
from audio_transcribe_azure import AzureAITranscriptionHIPAANode

# Create node
node = AzureAITranscriptionHIPAANode()

# Test with NON-PHI audio
result = node.transcribe_azure_hipaa(
    audio_path="/path/to/test_audio.wav",  # NOT patient data!
    azure_speech_key="YOUR_AZURE_KEY_HERE",
    azure_region="eastus",
    user_id="test_user",
    baa_confirmed=False,  # Set False for testing
    enable_audit_logging=False  # Disable for testing
)

print(result)
```

### Step 9: Production Deployment Checklist

Before processing real PHI:

- [ ] BAA signed with Microsoft
- [ ] BAA coverage verified
- [ ] Azure region is HIPAA-eligible (US region)
- [ ] Encryption enabled (in transit and at rest)
- [ ] Data retention disabled
- [ ] Access controls configured
- [ ] Diagnostic logging enabled
- [ ] Multi-factor authentication enabled
- [ ] Compliance team approval obtained
- [ ] Staff training completed
- [ ] Tested with non-PHI data
- [ ] Incident response plan documented

---

## Usage Guide

### Basic Usage in ComfyUI

1. **Start ComfyUI**

2. **Add Azure AI Transcription Node:**
   - Right-click → Add Node
   - Healthcare/PHI/Cloud → **Audio Transcription • Azure AI HIPAA**

3. **Configure Parameters:**
   - `audio_path`: `/secure/phi_audio/recording.wav`
   - `azure_speech_key`: Your Azure key (from Step 4)
   - `azure_region`: `eastus` (or your chosen region)
   - `user_id`: `dr_smith`
   - `baa_confirmed`: `True` ⚠️ Only after BAA is signed!
   - `patient_encounter_id`: `ENC123456`
   - `num_speakers`: `2`
   - `enable_diarization`: `True`
   - `enable_audit_logging`: `True`
   - `save_encrypted_output`: `True`

4. **Run Workflow**

5. **View Outputs:**
   - `transcription`: Full text
   - `diarized_text`: Text with speaker labels
   - `json_output`: Structured JSON data
   - `security_info`: Compliance status

### Python Script Usage

```python
import sys
sys.path.append('/path/to/ComfyUI/custom_nodes/ComfyUI-llama-cpp-cli')

from audio_transcribe_azure import AzureAITranscriptionHIPAANode

# Create node
node = AzureAITranscriptionHIPAANode()

# Transcribe with Azure AI
result = node.transcribe_azure_hipaa(
    audio_path="/secure/phi_audio/consultation.wav",
    azure_speech_key="your_azure_key_here",
    azure_region="eastus",
    user_id="dr_smith",
    baa_confirmed=True,  # Only True after BAA signed!
    patient_encounter_id="ENC123456",
    language="en-US",
    num_speakers=2,
    enable_diarization=True,
    save_encrypted_output=True,
    enable_audit_logging=True
)

transcription, diarized_text, json_output, security_info = result

print("=== TRANSCRIPTION ===")
print(transcription)
print("\n=== DIARIZED ===")
print(diarized_text)
print("\n=== SECURITY INFO ===")
print(security_info)
```

---

## Security Best Practices

### 1. Key Management

**DO:**
- Store keys in Azure Key Vault
- Use managed identities when possible
- Rotate keys regularly (quarterly)
- Use separate keys for dev/prod

**DON'T:**
- Commit keys to source control
- Share keys in email/chat
- Use same key across environments
- Hard-code keys in applications

**Example: Use Environment Variables**

```python
import os

# Store key in environment variable
azure_key = os.environ.get('AZURE_SPEECH_KEY')
azure_region = os.environ.get('AZURE_SPEECH_REGION', 'eastus')

# Use in node
result = node.transcribe_azure_hipaa(
    audio_path=audio_path,
    azure_speech_key=azure_key,
    azure_region=azure_region,
    # ... other params
)
```

```bash
# Set environment variables
export AZURE_SPEECH_KEY="your_key_here"
export AZURE_SPEECH_REGION="eastus"

# Run your application
python transcribe.py
```

### 2. Network Security

- Use Azure Virtual Networks (VNet)
- Configure Network Security Groups (NSG)
- Enable Azure Private Link for Speech Service
- Use VPN or ExpressRoute for on-premises access
- Enable Azure Firewall

### 3. Monitoring and Alerts

```
Set up alerts for:
- Unusual access patterns
- Failed authentication attempts
- Data access from unexpected regions
- High volume API usage
- Service errors
```

### 4. Regular Audits

**Monthly:**
- Review Azure activity logs
- Check access control assignments
- Verify no unauthorized API keys
- Review diagnostic logs

**Quarterly:**
- Security assessment
- Key rotation
- BAA compliance verification
- Update incident response plan

**Annually:**
- Full HIPAA compliance audit
- Penetration testing
- Update security policies
- Staff retraining

---

## Cost Estimation

### Azure AI Speech Pricing (as of 2024)

**Standard Tier (S0):**
- **Speech-to-Text:** $1.00 per audio hour
- **Speaker Diarization:** Included
- **First 5 hours free** per month

**Example Costs:**

| Usage | Hours/Month | Cost/Month |
|-------|-------------|------------|
| Small Clinic | 10 hours | $5.00 |
| Medium Clinic | 50 hours | $45.00 |
| Large Clinic | 200 hours | $195.00 |
| Hospital | 1000 hours | $995.00 |

**Cost Comparison:**

| Solution | Setup Cost | Monthly Cost (100 hrs) | Accuracy |
|----------|-----------|----------------------|----------|
| **Local (Whisper.cpp)** | $0 | $0 | Good |
| **Azure AI** | $0 | $95 | Excellent |

**When Azure is Cost-Effective:**
- Low to medium volume (< 200 hrs/month)
- Need best accuracy
- Want zero maintenance
- Enterprise support required

**When Local is Cost-Effective:**
- High volume (> 500 hrs/month)
- Have IT infrastructure
- Cost is primary concern
- Good accuracy acceptable

---

## Supported Languages

Azure AI Speech supports 100+ languages:

**Common Languages:**
- English (US): `en-US`
- English (UK): `en-GB`
- Spanish: `es-ES`, `es-MX`
- French: `fr-FR`
- German: `de-DE`
- Italian: `it-IT`
- Portuguese: `pt-BR`
- Chinese: `zh-CN`
- Japanese: `ja-JP`
- Korean: `ko-KR`

Full list: https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support

---

## Advanced Features

### 1. Custom Models (Medical Terminology)

Azure allows training custom speech models for medical terminology:

```
Benefits:
- Better recognition of medical terms
- Drug names, procedures, diagnoses
- Specialty-specific vocabulary
- Improved accuracy for healthcare
```

**Setup:**
1. Azure Portal → Speech Service → Custom Speech
2. Upload training data (medical transcripts)
3. Train custom model
4. Use custom model endpoint

### 2. Real-Time Transcription

For live consultations:

```python
# Azure supports real-time streaming transcription
# Useful for:
- Live consultations
- Telemedicine
- Real-time note-taking
- Instant feedback
```

### 3. Medical Conversation Insights

Azure offers medical-specific features:

- Medical entity extraction
- Medication recognition
- Diagnosis identification
- Clinical decision support

---

## Troubleshooting

### Error: "BAA not confirmed"

**Solution:**
Only set `baa_confirmed=True` after you've actually signed the BAA with Microsoft.

### Error: "Invalid subscription key"

**Solution:**
```
1. Check key is copied correctly (no extra spaces)
2. Verify region matches resource region
3. Ensure Speech Service is enabled
4. Check Azure subscription is active
```

### Error: "Region not available"

**Solution:**
Use HIPAA-eligible US regions: `eastus`, `eastus2`, `westus`, `westus2`, `centralus`

### Poor Transcription Quality

**Solutions:**
1. **Improve audio quality:**
   - Use better microphone
   - Reduce background noise
   - Ensure clear speech

2. **Optimize settings:**
   - Set correct language (`en-US` for US English)
   - Use appropriate audio format (WAV 16kHz recommended)

3. **Consider custom model:**
   - Train on your medical terminology
   - Better for specialty-specific language

### High Costs

**Solutions:**
1. **Optimize usage:**
   - Only transcribe necessary recordings
   - Use local transcription for non-critical audio
   - Batch processing during off-peak

2. **Consider hybrid approach:**
   - Azure for important consultations
   - Local for routine notes
   - Best of both worlds

---

## Compliance Documentation

### Records to Maintain

1. **BAA Documentation:**
   - Signed BAA with Microsoft
   - Execution date
   - Coverage details
   - Renewal dates

2. **Configuration Records:**
   - Azure region used
   - Encryption settings
   - Access control policies
   - Data retention policies

3. **Audit Logs:**
   - All PHI access (from local audit log)
   - Azure diagnostic logs
   - Access control changes
   - Security incidents

4. **Training Records:**
   - Staff HIPAA training
   - Azure security training
   - Incident response drills
   - Policy acknowledgments

---

## Comparison: Local vs Azure

| Feature | Local (Whisper.cpp) | Azure AI Speech |
|---------|-------------------|-----------------|
| **HIPAA Compliant** | ✅ Yes | ✅ Yes (with BAA) |
| **Accuracy** | Good (85-90%) | Excellent (95-98%) |
| **Speaker Diarization** | Basic | Advanced |
| **Medical Terminology** | Standard | Customizable |
| **Setup Complexity** | Medium | Easy |
| **Ongoing Cost** | $0 | $1/hour |
| **Infrastructure** | You maintain | Microsoft maintains |
| **Internet Required** | ❌ No | ✅ Yes |
| **BAA Required** | ❌ No | ✅ Yes |
| **Best For** | High volume, cost-sensitive | Best accuracy, enterprise |

---

## Support Resources

### Microsoft Resources:
- **Azure HIPAA Guide:** https://docs.microsoft.com/azure/compliance/offerings/offering-hipaa-us
- **Speech Service Docs:** https://docs.microsoft.com/azure/cognitive-services/speech-service/
- **BAA Request:** https://aka.ms/BAA
- **Service Trust Portal:** https://servicetrust.microsoft.com/

### Compliance Resources:
- **HHS HIPAA:** https://www.hhs.gov/hipaa
- **Azure Compliance:** https://azure.microsoft.com/en-us/explore/trusted-cloud/compliance/
- **Microsoft Trust Center:** https://www.microsoft.com/en-us/trust-center

### Support:
- **Azure Support:** Create ticket in Azure Portal
- **Enterprise Support:** Contact your Microsoft account team
- **Community:** Microsoft Q&A forums

---

## Next Steps

1. ✅ **Sign BAA with Microsoft** (CRITICAL)
2. ✅ **Create Azure Speech Service** (follow Step 3)
3. ✅ **Configure HIPAA settings** (follow Step 5)
4. ✅ **Test with non-PHI audio** (follow Step 8)
5. ✅ **Complete deployment checklist** (follow Step 9)
6. ✅ **Get compliance approval**
7. ✅ **Deploy for production**

---

**You now have enterprise-grade, HIPAA-compliant audio transcription with Microsoft Azure AI!**

Remember: Always maintain your BAA, monitor compliance, and keep audit logs for at least 6 years per HIPAA requirements.
