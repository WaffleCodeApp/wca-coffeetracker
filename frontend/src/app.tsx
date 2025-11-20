import { isAmplifyConfigured } from "./amplify_config";
import { AuthenticationProvider } from "./contexts/authentication/provider";
import { useContext, useState, useEffect } from "react";
import { AuthenticationContext } from "./contexts/authentication/context";
import { apiConfig } from "./api_config";
import { Authenticator } from "@aws-amplify/ui-react";

const HelloWorld = () => {
  const { fetchWithToken, idToken } = useContext(AuthenticationContext);
  const [data, setData] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHelloWorld = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Construct the URL using apiConfig
        // Path is already determined based on infrastructure config (includes service name and endpoint)
        console.log("🌐 [app] Constructing URL from apiConfig:", {
          protocol: apiConfig.aBackendService.protocol,
          host: apiConfig.aBackendService.host,
          path: apiConfig.aBackendService.path,
          full_config: apiConfig,
        });
        
        const url = `${apiConfig.aBackendService.protocol}${apiConfig.aBackendService.host}${apiConfig.aBackendService.path}`;
        console.log("🔗 [app] Final URL to fetch:", url);
        
        console.log("📤 [app] Making request with fetchWithToken...");
        const response = await fetchWithToken(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        console.log("📥 [app] Response received:", {
          ok: response.ok,
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
        });

        if (!response.ok) {
          const errorText = await response.text().catch(() => 'Unable to read error response');
          console.error("❌ [app] HTTP error response body:", errorText);
          throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
        }

        const result = await response.text();
        console.log("✅ [app] Successfully received response:", result);
        setData(result);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        console.error('❌ [app] Error fetching hello world:', {
          error: err,
          message: errorMessage,
          stack: err instanceof Error ? err.stack : undefined,
        });
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchHelloWorld();
  }, [fetchWithToken, idToken]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#d32f2f',
        textAlign: 'center',
        padding: '20px'
      }}>
        <div style={{ marginBottom: '10px' }}>❌ Error</div>
        <div>{error}</div>
      </div>
    );
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      fontSize: '24px',
      textAlign: 'center',
      padding: '20px'
    }}>
      <div style={{ marginBottom: '20px' }}>🌍 Hello World Response:</div>
      <div style={{ 
        backgroundColor: '#f5f5f5', 
        padding: '20px', 
        borderRadius: '8px',
        border: '1px solid #ddd',
        fontFamily: 'monospace',
        fontSize: '16px',
        color: '#000000'
      }}>
        {data}
      </div>
    </div>
  );
};

export const App = () => {
  // Show error if Amplify configuration failed
  if (!isAmplifyConfigured) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          fontSize: "16px",
          textAlign: "center",
          padding: "20px",
          maxWidth: "600px",
          margin: "0 auto",
        }}
      >
        <div
          style={{ marginBottom: "20px", color: "#d32f2f", fontSize: "20px" }}
        >
          ⚠️ Configuration Error
        </div>
        <div style={{ marginBottom: "20px" }}>
          Amplify configuration failed. Please check your environment variables.
        </div>
        <div style={{ fontSize: "14px", color: "#666" }}>
          See console for details and check your <code>.env</code> file.
        </div>
      </div>
    );
  }

  return (
    <Authenticator
      // Self-signup is disabled by default. Users must be created by an admin.
      // To enable self-signup:
      // 1. Remove the hideSignUp prop below (or set it to false)
      // 2. In infrastructure.json, set allowAdminCreateUserOnly to false in the 
      //    frontend authentication settings to enable self-signup on the backend side as well
      hideSignUp={true}
    >
      <AuthenticationProvider>
        <HelloWorld />
      </AuthenticationProvider>
    </Authenticator>
  );
};
