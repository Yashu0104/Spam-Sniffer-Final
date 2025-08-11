import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const envContent = `# Google OAuth2 Configuration
# Replace these with your actual Google API credentials
VITE_REACT_APP_CLIENT_ID=321887573250-cvd2ltaf4iqp1dklufl5u58au4m8778m.apps.googleusercontent.com
VITE_REACT_APP_API_KEY=AIzaSyDUnpga4m6hY2ItnHLy0IStmQe2_Q2JHbQ
VITE_REACT_APP_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify
`;

const envPath = path.join(__dirname, '.env');

try {
  fs.writeFileSync(envPath, envContent);
  console.log('✅ .env file created successfully!');
  console.log('📁 Location:', envPath);
} catch (error) {
  console.error('❌ Error creating .env file:', error.message);
}
