# MedXM.ai - Medical Experience Management Software

A comprehensive web application for generating professional medical/legal reports using AI-powered text transformation.

## Features

- **User Authentication**: Secure login and registration with specialty-based access
- **AI-Powered Report Generation**: Transform transcriptions and notes into professional medical/legal reports
- **Multiple Input Methods**:
  - Upload existing transcriptions
  - Upload point-form notes
  - Live transcription (to be fully implemented)
  - Direct note-taking
- **Specialty Support**: Supports 18+ medical specialties including mental health specialties
- **Content Refinement**: AI-powered content refinement with custom commands
- **Document Generation**: Automatic Microsoft Word document generation
- **Report Library**: Store and manage all generated reports
- **Privacy-Focused**: Automatically replaces patient names with generic terms during AI processing

## Tech Stack

- **Frontend**: Next.js 14 (App Router), React, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes
- **Database**: MongoDB
- **AI**: OpenAI GPT-4
- **Document Generation**: docx library
- **Authentication**: bcryptjs

## Prerequisites

- Node.js 18+ and npm
- MongoDB (local or Atlas)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd medxm-ai
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=mongodb://localhost:27017/medxm
```

4. Start MongoDB (if running locally):
```bash
mongod
```

5. Run the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### 1. Create Account
- Navigate to the home page
- Click "Create Account"
- Fill in your details including specialty type
- Click "Create Account"

### 2. Generate a Report
- Login with your credentials
- Click "Generate New Report" from the dashboard
- Configure report settings:
  - Report title
  - Claimant information
  - Perspective (first/third person)
  - Specialty type (if admin)

### 3. Complete Report Sections
For each section:
- Choose input method (upload transcription, upload notes, live input)
- Provide the information
- Click "Generate Content" to transform with AI
- (Optional) Refine the content with custom commands
- Click "Save & Continue to Next Section"

### 4. Process and Download
- After completing all sections, click "Finish & Process Report"
- Click "Process Report" to generate the Word document
- Download the report or view it in your library

## Report Sections

Standard sections (all specialties):
- Accident Details
- Initial Accident Complaints
- Current Complaints
- Course of Treatment
- Past Medical History
- Medications
- Childhood/Educational History
- Social History
- Functional Status
- Substance Use
- Occupational History
- Clinical Examination
- Question and Answer Section

Additional sections (Psychiatry/Psychology):
- Past Psychiatric History
- Family Psychiatric History
- Mental Health Screening

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Report Generation
- `POST /api/generate` - Generate content from input
- `POST /api/refine` - Refine generated content
- `POST /api/report/process` - Process and save complete report

### Report Management
- `GET /api/reports` - List all reports
- `GET /api/report/download/[id]` - Download report
- `DELETE /api/reports/[id]` - Delete report

## Project Structure

```
medxm-ai/
├── app/
│   ├── api/              # API routes
│   │   ├── auth/         # Authentication endpoints
│   │   ├── generate/     # AI generation endpoint
│   │   ├── refine/       # Content refinement endpoint
│   │   ├── report/       # Report processing endpoints
│   │   └── reports/      # Report management endpoints
│   ├── dashboard/        # Dashboard page
│   ├── library/          # Report library page
│   ├── report/           # Report creation pages
│   │   ├── new/          # Report configuration
│   │   ├── generate/     # Report generation workflow
│   │   └── process/      # Report processing
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Login/Register page
├── lib/
│   └── mongodb.ts        # Database connection
├── public/               # Static assets
├── .env.example          # Environment variables template
├── next.config.mjs       # Next.js configuration
├── package.json          # Dependencies
├── tailwind.config.ts    # Tailwind configuration
└── tsconfig.json         # TypeScript configuration
```

## Deployment

### Vercel (Recommended)
1. Push your code to GitHub
2. Connect your repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy

### Other Platforms
1. Build the application:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

## Future Enhancements

- Real-time transcription integration (speech-to-text)
- Report summary generation (requires larger token context)
- User-specific report filtering
- Report templates
- Collaborative editing
- Export to PDF
- Multi-language support
- Advanced analytics

## Security Notes

- User passwords are hashed with bcrypt
- Patient names are automatically replaced with generic terms during AI processing
- Environment variables should never be committed to version control
- Implement proper authentication middleware for production
- Add rate limiting for API endpoints
- Use HTTPS in production

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
