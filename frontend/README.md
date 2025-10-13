# React/TypeScript Static Frontend with AWS Authentication

A production-ready React/TypeScript static frontend starter code designed for deployment on AWS S3 with CloudFront distribution, featuring AWS Cognito authentication and IAM-signed API calls.

## Overview

This starter code provides a complete foundation for building static web applications with React/TypeScript that are:

- **Deployment-ready**: Configured for AWS S3 + CloudFront with SSL and custom domains
- **Authentication-enabled**: Integrated with AWS Cognito User Pool and Hosted UI
- **API-ready**: Includes IAM-signed requests to API Gateway endpoints
- **Production-grade**: Includes proper error handling, TypeScript support, and optimized builds

## Architecture

The frontend is deployed using AWS infrastructure with the following components:

- **Static Hosting**: S3 bucket with website hosting enabled
- **CDN**: CloudFront distribution with SSL/TLS termination
- **Authentication**: AWS Cognito User Pool with Hosted UI
- **API Integration**: IAM-signed requests to API Gateway (REST v1 or HTTP v2)
- **CICD**: AWS CodePipeline for automated builds and deployments
- **Security**: WAF protection and proper CORS handling

## Project Structure

```
react/
├── src/
│   ├── app.tsx                    # Main application component
│   ├── main.tsx                   # Application entry point
│   ├── amplify_config.ts          # AWS Amplify configuration
│   ├── api_config.ts              # API endpoint configuration
│   └── contexts/
│       └── authentication/        # Authentication context and providers
│           ├── provider.tsx       # Authentication provider component
│           ├── context.ts         # React context definition
│           ├── type.ts            # TypeScript type definitions
│           ├── cognito.ts         # Cognito configuration
│           └── auth_check.tsx     # Authentication state management
├── public/                        # Static assets
├── build.sh                       # Build script for CICD
├── package.json                   # Dependencies and scripts
├── vite.config.ts                 # Vite build configuration
└── README.md                      # This file
```

## Key Features

### 1. Authentication
- **Cognito Integration**: Uses AWS Cognito User Pool with Hosted UI
- **Automatic Redirects**: Seamless login/logout flow with proper redirects
- **Token Management**: Automatic token refresh and session management
- **User Context**: Global authentication state available throughout the app

### 2. API Integration
- **IAM Signing**: Automatic AWS IAM signature for API Gateway requests
- **SigV4 Authentication**: Proper AWS signature version 4 implementation
- **Credential Management**: Automatic credential retrieval from Cognito Identity Pool
- **Type Safety**: Full TypeScript support for API calls

### 3. Production Features
- **Optimized Builds**: Vite-based build system with code splitting
- **Environment Configuration**: Build-time environment variable injection
- **Error Handling**: Comprehensive error boundaries and user feedback
- **Responsive Design**: Mobile-friendly UI components

## Environment Variables

The application expects the following environment variables (automatically set by CICD):

| Variable | Description | Source |
|----------|-------------|---------|
| `VITE_AWS_USER_POOL_ID` | Cognito User Pool ID | CICD |
| `VITE_AWS_USER_POOL_CLIENT_ID` | Cognito User Pool Client ID | CICD |
| `VITE_AWS_COGNITO_DOMAIN` | Cognito Hosted UI Domain | CICD |
| `VITE_AWS_COGNITO_REGION` | AWS Region for Cognito | CICD |
| `VITE_AWS_COGNITO_IDENTITY_POOL_ID` | Cognito Identity Pool ID | CICD |
| `VITE_HTTP_API_V2_HOST` | API Gateway HTTP v2 Hostname | CICD |
| `VITE_REST_API_V1_HOST` | API Gateway REST v1 Hostname | CICD |
| `VITE_AWS_PROJECT_REGION` | AWS Region | CICD |
| `VITE_DEPLOYMENT_DOMAIN_NAME` | Deployment Domain | CICD |
| `VITE_PIPELINE_ID` | Pipeline ID | CICD |

## Development

### Prerequisites
- Node.js 18+ (recommended: 22)
- npm or yarn
- AWS CLI (for local testing)

### Local Development

1. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env.local
   ```

3. **Configure environment variables** in `.env.local`:
   ```env
   VITE_AWS_USER_POOL_ID=your-user-pool-id
   VITE_AWS_USER_POOL_CLIENT_ID=your-client-id
   VITE_AWS_COGNITO_DOMAIN=your-cognito-domain
   VITE_AWS_COGNITO_REGION=us-east-1
   VITE_AWS_COGNITO_IDENTITY_POOL_ID=your-identity-pool-id
   VITE_HTTP_API_V2_HOST=your-api-gateway-host
   VITE_AWS_PROJECT_REGION=us-east-1
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Access the application**:
   - Local: `http://localhost:5173`
   - The app will automatically redirect to Cognito Hosted UI for authentication

### Testing API Integration

The sample app makes a call to a fictional `my_container` service endpoint. To test with a real API:

1. **Update API configuration** in `src/api_config.ts`:
   ```typescript
   export const apiConfig = {
     my_container: {
       protocol: "https://",
       host: import.meta.env.VITE_HTTP_API_V2_HOST,
       path: "/your-actual-service", // Update this path
     },
     region: import.meta.env.VITE_AWS_PROJECT_REGION,
   };
   ```

2. **Update the API call** in `src/app.tsx`:
   ```typescript
   const url = `${apiConfig.my_container.protocol}${apiConfig.my_container.host}${apiConfig.my_container.path}/your-endpoint`;
   ```

## Deployment

### Infrastructure Requirements

This frontend requires the following AWS infrastructure (deployed via CloudFormation):

- **S3 Bucket**: Static website hosting with public read access
- **CloudFront Distribution**: CDN with SSL/TLS termination
- **Route53**: DNS management (optional, for custom domains)
- **Cognito User Pool**: User authentication and management
- **Cognito Identity Pool**: AWS credential federation
- **CodePipeline**: CICD pipeline for automated deployments
- **WAF**: Web Application Firewall (optional)

### Deployment Process

1. **Code Push**: Push code to the configured Git repository
2. **Build**: CodePipeline triggers CodeBuild to create optimized static assets
3. **Deploy**: Assets are uploaded to S3 and CloudFront cache is invalidated
4. **SSL**: Automatic SSL certificate provisioning for custom domains

### Configuration

The frontend automatically configures itself using:
- **Environment Variables**: Injected during build process
- **Cognito Settings**: Retrieved from SSM parameters
- **API Endpoints**: Configured based on deployment environment

## Authentication Flow

### 1. Initial Load
- App checks for existing authentication session
- If not authenticated, redirects to Cognito Hosted UI

### 2. Cognito Hosted UI
- User logs in via Cognito Hosted UI
- Cognito redirects back to app with authorization code
- App exchanges code for tokens

### 3. Token Management
- ID token stored for user identification
- Access token used for API calls
- Automatic token refresh before expiration

### 4. API Calls
- Uses `signedFetch` for IAM-signed requests
- Automatically includes AWS credentials
- Handles token refresh and error scenarios

## API Integration

### Making Authenticated API Calls

```typescript
import { useContext } from 'react';
import { AuthenticationContext } from './contexts/authentication/context';

const MyComponent = () => {
  const { signedFetch, idToken } = useContext(AuthenticationContext);

  const callAPI = async () => {
    try {
      const response = await signedFetch('https://api.example.com/endpoint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`,
        },
        body: JSON.stringify({ data: 'example' }),
      });
      
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('API call failed:', error);
    }
  };
};
```

### API Configuration

Configure API endpoints in `src/api_config.ts`:

```typescript
export const apiConfig = {
  my_service: {
    protocol: "https://",
    host: import.meta.env.VITE_HTTP_API_V2_HOST,
    path: "/my_service",
  },
  another_service: {
    protocol: "https://",
    host: import.meta.env.VITE_REST_API_V1_HOST,
    path: "/another_service",
  },
  region: import.meta.env.VITE_AWS_PROJECT_REGION,
};
```

## Security

- **HTTPS Only**: All traffic encrypted in transit
- **Cognito Security**: Industry-standard OAuth 2.0 / OpenID Connect
- **IAM Permissions**: Least-privilege access to AWS services
- **WAF Protection**: Optional Web Application Firewall
- **CORS Configuration**: Proper cross-origin resource sharing
- **Token Security**: Secure token storage and transmission

## Monitoring

- **CloudWatch Logs**: Application logs and errors
- **CloudFront Metrics**: CDN performance and usage
- **Cognito Analytics**: Authentication events and user behavior
- **Build Logs**: CodeBuild execution logs

## Customization

### Adding New Pages

1. **Create page component**:
   ```typescript
   // src/pages/NewPage.tsx
   import { useContext } from 'react';
   import { AuthenticationContext } from '../contexts/authentication/context';

   export const NewPage = () => {
     const { user, signedFetch } = useContext(AuthenticationContext);
     
     return (
       <div>
         <h1>New Page</h1>
         <p>Welcome, {user?.username}!</p>
       </div>
     );
   };
   ```

2. **Add routing** (if using React Router):
   ```typescript
   import { NewPage } from './pages/NewPage';
   
   // Add route configuration
   ```

### Custom Authentication

Extend the authentication context for additional features:

```typescript
// src/contexts/authentication/type.ts
export type AuthenticationContextType = {
  // Existing properties...
  customMethod: () => Promise<void>;
  customState: string | null;
};
```

### Environment-Specific Configuration

Add new environment variables in `vite.config.ts`:

```typescript
define: {
  "import.meta.env.VITE_CUSTOM_VAR": JSON.stringify(
    process.env.VITE_CUSTOM_VAR
  ),
}
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify Cognito configuration in environment variables
   - Check redirect URIs in Cognito User Pool Client
   - Ensure proper CORS configuration

2. **API Call Failures**:
   - Verify API Gateway endpoint configuration
   - Check IAM permissions for the Identity Pool
   - Ensure proper API Gateway CORS settings

3. **Build Failures**:
   - Check environment variable configuration
   - Verify Node.js version compatibility
   - Review build logs for specific errors

4. **Deployment Issues**:
   - Verify S3 bucket permissions
   - Check CloudFront distribution status
   - Review CodePipeline execution logs

### Debug Mode

Enable debug logging by adding to your environment:

```env
VITE_DEBUG=true
```

### Logs

- **Application Logs**: Browser console and CloudWatch
- **Build Logs**: CodeBuild logs in CloudWatch
- **Deployment Logs**: CodePipeline execution logs

## Performance Optimization

### Build Optimizations
- **Code Splitting**: Automatic vendor and route-based splitting
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Image and CSS optimization
- **Bundle Analysis**: Use `npm run build -- --analyze` for bundle analysis

### Runtime Optimizations
- **Lazy Loading**: Component and route-based lazy loading
- **Memoization**: React.memo and useMemo for expensive operations
- **Caching**: CloudFront caching for static assets

## Support

For issues and questions:
1. Check browser console for client-side errors
2. Review CloudWatch logs for server-side issues
3. Verify environment variables and Cognito configuration
4. Consult the main Waffle documentation

---

This starter code provides a solid foundation for building production-ready React applications with AWS integration. Customize the components, styling, and business logic as needed for your specific use case.